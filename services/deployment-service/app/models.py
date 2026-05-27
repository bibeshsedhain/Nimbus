from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FunctionUploadResponse(BaseModel):
    function_id: str
    filename: str
    created_at: datetime


class DeploymentSummary(BaseModel):
    function_id: str
    filename: str
    created_at: datetime
    execution_count: int = 0


class ExecutionRequest(BaseModel):
    event: dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    execution_id: str
    function_id: str
    status: str
    exit_code: int
    stdout: str
    stderr: str
    result: Any | None = None
    duration_ms: int
    image_tag: str
    created_at: datetime | None = None


class ExecutionSummary(BaseModel):
    execution_id: str
    function_id: str
    status: str
    exit_code: int
    duration_ms: int
    created_at: datetime
