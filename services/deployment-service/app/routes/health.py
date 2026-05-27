from fastapi import APIRouter

from app.engine.executor import DockerExecutor

router = APIRouter(tags=["health"])
executor = DockerExecutor()


@router.get("/health")
async def health() -> dict:
    docker_ok = executor.ping()
    return {
        "status": "ok" if docker_ok else "degraded",
        "docker": docker_ok,
    }
