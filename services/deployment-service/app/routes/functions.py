import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import require_api_key
from app.engine.executor import get_executor
from app.engine.workspace import FunctionWorkspace
from app.models import (
    DeploymentSummary,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionSummary,
    FunctionUploadResponse,
)
from app.services import deployments as deployment_service

router = APIRouter(
    prefix="/v1/functions",
    tags=["functions"],
    dependencies=[Depends(require_api_key)],
)

workspace = FunctionWorkspace()


@router.get("", response_model=list[DeploymentSummary])
def list_functions(db: Session = Depends(get_db)) -> list[DeploymentSummary]:
    items = deployment_service.list_deployments(db)
    return [
        DeploymentSummary(
            function_id=item.id,
            filename=item.filename,
            created_at=item.created_at,
            execution_count=len(item.executions),
        )
        for item in items
    ]


@router.get("/{function_id}", response_model=DeploymentSummary)
def get_function(function_id: str, db: Session = Depends(get_db)) -> DeploymentSummary:
    deployment = deployment_service.get_deployment(db, function_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail=f"Function '{function_id}' not found")
    return DeploymentSummary(
        function_id=deployment.id,
        filename=deployment.filename,
        created_at=deployment.created_at,
        execution_count=len(deployment.executions),
    )


@router.post("", response_model=FunctionUploadResponse, status_code=201)
async def upload_function(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> FunctionUploadResponse:
    if not file.filename or not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are supported")

    source = (await file.read()).decode("utf-8")
    if "def handler" not in source:
        raise HTTPException(
            status_code=400,
            detail="function.py must define handler(event, context)",
        )

    function_id = str(uuid.uuid4())
    workspace.create(source, filename="function.py", function_id=function_id)
    deployment = deployment_service.create_deployment(
        db, function_id, filename="function.py", source_code=source
    )

    return FunctionUploadResponse(
        function_id=deployment.id,
        filename=deployment.filename,
        created_at=deployment.created_at,
    )


@router.post("/{function_id}/execute", response_model=ExecutionResponse)
async def execute_function(
    function_id: str,
    body: ExecutionRequest | None = None,
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    event = body.event if body else {}

    deployment = deployment_service.get_deployment(db, function_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail=f"Function '{function_id}' not found")

    try:
        work_dir = workspace.get_dir(function_id)
    except FileNotFoundError:
        workspace.create(
            deployment.source_code,
            filename=deployment.filename,
            function_id=function_id,
        )
        work_dir = workspace.get_dir(function_id)

    executor = get_executor()
    if not executor.ping():
        raise HTTPException(
            status_code=503,
            detail="Docker daemon is not available. Start Docker Desktop and try again.",
        )

    outcome = executor.execute(work_dir, function_id, event)
    execution = deployment_service.create_execution(
        db,
        function_id,
        status=outcome["status"],
        exit_code=outcome["exit_code"],
        stdout=outcome["stdout"],
        stderr=outcome["stderr"],
        result=outcome["result"],
        duration_ms=outcome["duration_ms"],
        image_tag=outcome["image_tag"],
        event=event,
    )

    return ExecutionResponse(
        execution_id=execution.id,
        function_id=function_id,
        created_at=execution.created_at,
        **{k: outcome[k] for k in ("status", "exit_code", "stdout", "stderr", "result", "duration_ms", "image_tag")},
    )


@router.get("/{function_id}/executions", response_model=list[ExecutionSummary])
def list_function_executions(
    function_id: str,
    db: Session = Depends(get_db),
) -> list[ExecutionSummary]:
    deployment = deployment_service.get_deployment(db, function_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail=f"Function '{function_id}' not found")

    executions = deployment_service.list_executions(db, function_id)
    return [
        ExecutionSummary(
            execution_id=item.id,
            function_id=item.deployment_id,
            status=item.status,
            exit_code=item.exit_code,
            duration_ms=item.duration_ms,
            created_at=item.created_at,
        )
        for item in executions
    ]


@router.get("/{function_id}/executions/{execution_id}", response_model=ExecutionResponse)
def get_function_execution(
    function_id: str,
    execution_id: str,
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    execution = deployment_service.get_execution(db, execution_id)
    if execution is None or execution.deployment_id != function_id:
        raise HTTPException(status_code=404, detail="Execution not found")

    return ExecutionResponse(
        execution_id=execution.id,
        function_id=execution.deployment_id,
        status=execution.status,
        exit_code=execution.exit_code,
        stdout=execution.stdout,
        stderr=execution.stderr,
        result=execution.result,
        duration_ms=execution.duration_ms,
        image_tag=execution.image_tag,
        created_at=execution.created_at,
    )


@router.delete("/{function_id}", status_code=204)
async def delete_function(function_id: str, db: Session = Depends(get_db)) -> None:
    deployment = deployment_service.get_deployment(db, function_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail=f"Function '{function_id}' not found")

    try:
        workspace.delete(function_id)
    except FileNotFoundError:
        pass

    deployment_service.delete_deployment(db, deployment)
