#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  python -m pip install --upgrade uv
fi

uv sync "$@"
