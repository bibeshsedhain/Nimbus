from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NIMBUS_", env_file=".env", extra="ignore")

    workspace_dir: Path = Path("/tmp/nimbus/functions")
    python_image: str = "python:3.12-slim"
    execution_timeout_seconds: int = 30
    container_memory_mb: int = 256
    container_cpus: float = 0.5
    cleanup_images: bool = True

    database_url: str = "postgresql+psycopg2://nimbus:nimbus@localhost:5432/nimbus"
    redis_url: str = "redis://localhost:6379/0"
    api_key: str | None = None
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
