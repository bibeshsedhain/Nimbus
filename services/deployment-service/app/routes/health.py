from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.engine.executor import get_executor

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    docker_ok = get_executor().ping()
    db_ok = False
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            db_ok = True
    except SQLAlchemyError:
        db_ok = False

    healthy = docker_ok and db_ok
    return {
        "status": "ok" if healthy else "degraded",
        "docker": docker_ok,
        "database": db_ok,
    }
