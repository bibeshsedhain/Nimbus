from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.engine.executor import DockerExecutor
from app.engine.workspace import FunctionWorkspace
from app.models import (
    ExecutionRequest,
    ExecutionResponse,
    FunctionUploadResponse,
)

router = APIRouter(prefix="/v1/functions", tags=["functions"])

workspace = FunctionWorkspace()
executor = DockerExecutor()


@router.post("", response_model=FunctionUploadResponse, status_code=201)
async def upload_function(file: UploadFile = File(...)) -> FunctionUploadResponse:
    if not file.filename or not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are supported")

    source = (await file.read()).decode("utf-8")
    if "def handler" not in source:
        raise HTTPException(
            status_code=400,
            detail="function.py must define handler(event, context)",
        )

    function_id = workspace.create(source, filename="function.py")
    return FunctionUploadResponse(
        function_id=function_id,
        filename="function.py",
        created_at=datetime.now(timezone.utc),
    )


@router.post("/{function_id}/execute", response_model=ExecutionResponse)
async def execute_function(
    function_id: str,
    body: ExecutionRequest | None = None,
) -> ExecutionResponse:
    event = body.event if body else {}

    try:
        work_dir = workspace.get_dir(function_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not executor.ping():
        raise HTTPException(
            status_code=503,
            detail="Docker daemon is not available",
        )

    outcome = executor.execute(work_dir, function_id, event)
    return ExecutionResponse(function_id=function_id, **outcome)


@router.delete("/{function_id}", status_code=204)
async def delete_function(function_id: str) -> None:
    try:
        workspace.delete(function_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
