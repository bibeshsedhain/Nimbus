RUNNER_TEMPLATE = '''\
import json
import os
import sys
import traceback
import importlib.util


def load_handler():
    spec = importlib.util.spec_from_file_location("user_function", "function.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load function.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "handler"):
        raise AttributeError("function.py must define a handler(event, context) function")
    return module.handler


def main() -> int:
    event_raw = os.environ.get("NIMBUS_EVENT", "{}")
    try:
        event = json.loads(event_raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid NIMBUS_EVENT JSON"}), file=sys.stderr)
        return 1

    context = {"request_id": os.environ.get("NIMBUS_REQUEST_ID", "")}

    try:
        handler = load_handler()
        result = handler(event, context)
        print(json.dumps({"result": result}))
        return 0
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def generate_dockerfile(python_image: str) -> str:
    return f"""FROM {python_image}
WORKDIR /app
COPY function.py .
COPY runner.py .
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python", "runner.py"]
"""


def write_build_context(work_dir, python_image: str) -> None:
    (work_dir / "Dockerfile").write_text(
        generate_dockerfile(python_image), encoding="utf-8"
    )
    (work_dir / "runner.py").write_text(RUNNER_TEMPLATE, encoding="utf-8")
