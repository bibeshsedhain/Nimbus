from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NIMBUS_")

    workspace_dir: Path = Path("/tmp/nimbus/functions")
    python_image: str = "python:3.12-slim"
    execution_timeout_seconds: int = 30
    container_memory_mb: int = 256
    container_cpus: float = 0.5
    cleanup_images: bool = True


settings = Settings()
