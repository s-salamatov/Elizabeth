#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend_spa"

cd "${FRONTEND_DIR}"

# Install node dependencies on demand to mirror CI without redoing work
if [ ! -d "node_modules" ] || [ ! -x "node_modules/.bin/eslint" ]; then
  echo "[frontend] Installing npm dependencies via npm ci..."
  npm ci
else
  echo "[frontend] node_modules present, skipping npm ci"
fi

# Ensure Playwright browsers are available (matches CI step)
if [ ! -d "node_modules/.cache/ms-playwright" ]; then
  echo "[frontend] Installing Playwright browsers..."
  npx playwright install --with-deps
else
  echo "[frontend] Playwright browsers already installed, skipping"
fi

echo "[frontend] Running lint..."
npm run lint

echo "[frontend] Running unit tests..."
npm run test

echo "[frontend] Running build..."
npm run build

# CI installs Python deps before e2e; assume env already prepared locally
if [ -d "${ROOT_DIR}/.venv" ]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

echo "[frontend] Running e2e tests..."
npm run e2e
