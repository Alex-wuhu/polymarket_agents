#!/usr/bin/env bash
set -euo pipefail

uv run python -c "from polymarket_agents.settings.env import load_env; load_env()"
uv run fastapi dev polymarket_agents/api/app.py
