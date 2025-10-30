"""Very small logging helper with runtime on/off control."""

from __future__ import annotations

import os
from typing import Any

_enabled: bool = os.getenv("POLYMARKET_LOGGING", "1").lower() not in {
    "0",
    "false",
    "off",
}


def enable_logging(enabled: bool = True) -> None:
    """Globally toggle logging output."""
    global _enabled
    _enabled = bool(enabled)


def is_enabled() -> bool:
    """Return current logging state."""
    return _enabled


def log(*values: Any, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
    """Print values when logging is enabled."""
    if not _enabled:
        return

    print(*values, sep=sep, end=end, flush=flush)
