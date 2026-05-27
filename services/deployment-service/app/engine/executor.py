import json
import time
import uuid
from pathlib import Path
from typing import Any

import docker
from docker.errors import DockerException

from app.config import settings
from app.engine.dockerfile import write_build_context


class DockerExecutor:
    def __init__(self) -> None:
        self._client: docker.DockerClient | None = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    def build_image(self, work_dir: Path, function_id: str) -> str:
        image_tag = f"nimbus-fn-{function_id[:8]}:{uuid.uuid4().hex[:12]}"
        write_build_context(work_dir, settings.python_image)

        image, build_logs = self.client.images.build(
            path=str(work_dir),
            tag=image_tag,
            rm=True,
            forcerm=True,
        )
        _ = build_logs  # consume generator side effects
        return image.tags[0] if image.tags else image_tag

    def run_container(
        self,
        image_tag: str,
        event: dict[str, Any],
        request_id: str,
    ) -> dict[str, Any]:
        container = self.client.containers.run(
            image_tag,
            detach=True,
            environment={
                "NIMBUS_EVENT": json.dumps(event),
                "NIMBUS_REQUEST_ID": request_id,
            },
            mem_limit=f"{settings.container_memory_mb}m",
            nano_cpus=int(settings.container_cpus * 1e9),
            network_disabled=True,
            read_only=True,
            tmpfs={"/tmp": "size=64m"},
        )

        start = time.perf_counter()
        try:
            result = container.wait(timeout=settings.execution_timeout_seconds)
            exit_code = result.get("StatusCode", 1)
        except Exception:
            container.kill()
            exit_code = 137
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            stdout = container.logs(stdout=True, stderr=False).decode(
                "utf-8", errors="replace"
            )
            stderr = container.logs(stdout=False, stderr=True).decode(
                "utf-8", errors="replace"
            )
            container.remove(force=True)

        parsed_result = None
        if exit_code == 0 and stdout.strip():
            try:
                payload = json.loads(stdout.strip().splitlines()[-1])
                parsed_result = payload.get("result")
            except json.JSONDecodeError:
                pass

        status = "success" if exit_code == 0 else "failed"
        if exit_code == 137:
            status = "timeout"

        return {
            "status": status,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "result": parsed_result,
            "duration_ms": duration_ms,
        }

    def execute(self, work_dir: Path, function_id: str, event: dict[str, Any]) -> dict[str, Any]:
        image_tag = self.build_image(work_dir, function_id)
        request_id = str(uuid.uuid4())

        try:
            outcome = self.run_container(image_tag, event, request_id)
            outcome["image_tag"] = image_tag
            return outcome
        finally:
            if settings.cleanup_images:
                self._remove_image(image_tag)

    def _remove_image(self, image_tag: str) -> None:
        try:
            self.client.images.remove(image=image_tag, force=True)
        except DockerException:
            pass

    def ping(self) -> bool:
        try:
            self.client.ping()
            return True
        except (DockerException, OSError):
            return False


_executor: DockerExecutor | None = None


def get_executor() -> DockerExecutor:
    global _executor
    if _executor is None:
        _executor = DockerExecutor()
    return _executor
