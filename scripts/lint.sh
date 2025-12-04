#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[lint.sh] Delegating to check_backend.sh and check_frontend.sh"
"${ROOT_DIR}/scripts/check_backend.sh"
"${ROOT_DIR}/scripts/check_frontend.sh"
