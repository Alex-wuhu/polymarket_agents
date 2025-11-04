"""Centralized helpers for loading environment variables at runtime."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_env(dotenv_path: str | os.PathLike[str] | None = None) -> None:
    """Load environment variables from the provided .env path or the project root."""
    candidate = Path(dotenv_path) if dotenv_path else Path.cwd() / ".env"
    if candidate.exists():
        load_dotenv(dotenv_path=str(candidate))


__all__ = ["load_env"]
