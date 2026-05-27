from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Deployment, Execution


def create_deployment(
    db: Session,
    deployment_id: str,
    filename: str,
    source_code: str,
) -> Deployment:
    deployment = Deployment(id=deployment_id, filename=filename, source_code=source_code)
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    return deployment


def get_deployment(db: Session, deployment_id: str) -> Deployment | None:
    stmt = (
        select(Deployment)
        .options(selectinload(Deployment.executions))
        .where(Deployment.id == deployment_id)
    )
    return db.scalar(stmt)


def list_deployments(db: Session, limit: int = 50) -> list[Deployment]:
    stmt = (
        select(Deployment)
        .options(selectinload(Deployment.executions))
        .order_by(Deployment.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def delete_deployment(db: Session, deployment: Deployment) -> None:
    db.delete(deployment)
    db.commit()


def create_execution(
    db: Session,
    deployment_id: str,
    *,
    status: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    result,
    duration_ms: int,
    image_tag: str,
    event: dict,
) -> Execution:
    execution = Execution(
        deployment_id=deployment_id,
        status=status,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        result=result,
        duration_ms=duration_ms,
        image_tag=image_tag,
        event=event,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def list_executions(db: Session, deployment_id: str, limit: int = 50) -> list[Execution]:
    stmt = (
        select(Execution)
        .where(Execution.deployment_id == deployment_id)
        .order_by(Execution.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_execution(db: Session, execution_id: str) -> Execution | None:
    return db.get(Execution, execution_id)
