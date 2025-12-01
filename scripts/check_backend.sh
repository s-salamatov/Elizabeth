#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# Activate virtualenv if present
if [ -d "${ROOT_DIR}/.venv" ]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

export DJANGO_SETTINGS_MODULE="elizabeth.elizabeth.settings.dev"
export PYTHONPATH="${PYTHONPATH:-}:${ROOT_DIR}"

echo "[backend] Running Django migrations..."
python manage.py migrate --noinput

echo "[backend] Running Django system check..."
python manage.py check

echo "[backend] Running black..."
black --check .

echo "[backend] Running isort..."
isort --check-only . --skip node_modules --skip frontend_spa/node_modules --skip .venv

echo "[backend] Running flake8..."
flake8 . --exclude node_modules,frontend_spa/node_modules,.venv

echo "[backend] Running mypy..."
mypy .

echo "[backend] Running pytest..."
pytest
