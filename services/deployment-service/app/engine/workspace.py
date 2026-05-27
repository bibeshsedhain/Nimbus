import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


class FunctionWorkspace:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.workspace_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create(self, source_code: str, filename: str = "function.py") -> str:
        function_id = str(uuid.uuid4())
        work_dir = self.base_dir / function_id
        work_dir.mkdir(parents=True, exist_ok=False)

        (work_dir / filename).write_text(source_code, encoding="utf-8")
        metadata = {
            "function_id": function_id,
            "filename": filename,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        (work_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        return function_id

    def get_dir(self, function_id: str) -> Path:
        work_dir = self.base_dir / function_id
        if not work_dir.is_dir():
            raise FileNotFoundError(f"Function '{function_id}' not found")
        return work_dir

    def get_metadata(self, function_id: str) -> dict:
        metadata_path = self.get_dir(function_id) / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata for '{function_id}' not found")
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def delete(self, function_id: str) -> None:
        work_dir = self.get_dir(function_id)
        shutil.rmtree(work_dir)
