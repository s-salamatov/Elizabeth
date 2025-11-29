#!/usr/bin/env bash
set -e

black . --check
isort . --check-only
flake8 .
mypy elizabeth
