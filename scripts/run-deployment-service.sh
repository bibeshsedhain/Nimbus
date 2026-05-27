#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_DIR="$ROOT/services/deployment-service"

cd "$SERVICE_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt

export NIMBUS_WORKSPACE_DIR="${NIMBUS_WORKSPACE_DIR:-/tmp/nimbus/functions}"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
