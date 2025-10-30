"""Simple colored logger with runtime toggles."""

from __future__ import annotations

import os
import sys
from typing import Any

_LEVELS = {"debug": 0, "print": 1, "error": 2}
_COLOR_CODES = {
    "debug": "\033[90m",  # Bright black / gray
    "print": "\033[96m",  # Cyan
    "error": "\033[91m",  # Red
}
_RESET = "\033[0m"


def _detect_default_level() -> int:
    raw_level = os.getenv("POLYMARKET_LOG_LEVEL", "print").lower()
    return _LEVELS.get(raw_level, _LEVELS["print"])


_enabled: bool = os.getenv("POLYMARKET_LOGGING", "1").lower() not in {
    "0",
    "false",
    "off",
}
_current_level: int = _detect_default_level()
_color_enabled: bool = os.getenv("NO_COLOR") is None and (
    (hasattr(sys.stdout, "isatty") and sys.stdout.isatty())
    or (hasattr(sys.stderr, "isatty") and sys.stderr.isatty())
)


def enable_logging(enabled: bool = True) -> None:
    """Globally toggle non-error logging output."""
    global _enabled
    _enabled = bool(enabled)


def is_enabled() -> bool:
    """Return current non-error logging state."""
    return _enabled


def set_log_level(level: str) -> None:
    """Adjust minimum log level (`debug`, `print`, `error`)."""
    global _current_level
    normalized = level.lower()
    if normalized not in _LEVELS:
        raise ValueError(f"Unknown log level: {level}")
    _current_level = _LEVELS[normalized]


def get_log_level() -> str:
    """Return current log level name."""
    for name, value in _LEVELS.items():
        if value == _current_level:
            return name
    return "print"


def _should_emit(level: str) -> bool:
    if level == "error":
        return True  # Always surface errors.
    return _enabled and _LEVELS[level] >= _current_level


def _format(level: str, message: str) -> str:
    if not message:
        return message
    if not _color_enabled:
        if level == "print":
            return message
        return f"[{level.upper()}] {message}"
    color = _COLOR_CODES[level]
    if level == "print":
        return f"{color}{message}{_RESET}"
    return f"{color}[{level.upper()}] {message}{_RESET}"


def _emit(
    level: str,
    *values: Any,
    sep: str = " ",
    end: str = "\n",
    flush: bool = False,
) -> None:
    if not _should_emit(level):
        return
    message = sep.join(str(value) for value in values)
    formatted = _format(level, message)
    target = sys.stderr if level == "error" else sys.stdout
    print(formatted, end=end, file=target, flush=flush)


def debug(*values: Any, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
    """Emit debug-level diagnostic output."""
    _emit("debug", *values, sep=sep, end=end, flush=flush)


def print_log(
    *values: Any, sep: str = " ", end: str = "\n", flush: bool = False
) -> None:
    """Emit user-facing informational output."""
    _emit("print", *values, sep=sep, end=end, flush=flush)


def error(*values: Any, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
    """Emit error output."""
    _emit("error", *values, sep=sep, end=end, flush=flush)


# Backwards compatibility alias.
log = print_log
