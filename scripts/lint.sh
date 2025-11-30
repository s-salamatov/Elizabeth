#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export DJANGO_SETTINGS_MODULE="elizabeth.elizabeth.settings.dev"
export PYTHONPATH="${PYTHONPATH:-}:${ROOT_DIR}"

cd "${ROOT_DIR}"

pushd frontend_spa >/dev/null
npm ci
npm run build
popd >/dev/null

python manage.py check
black . --check
isort . --check-only
flake8 .
mypy .
pytest
