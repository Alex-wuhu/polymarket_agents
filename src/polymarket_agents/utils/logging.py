"""Simple colored logger with runtime toggles."""

from __future__ import annotations

import os
import sys
from typing import Any

try:
    from polymarket_agents.settings.env import load_env as _load_env
except ImportError:  # pragma: no cover - fallback when module unavailable
    _load_env = None

_VERBOSITY_LEVELS = ("print", "debug")
_VERBOSITY_INDEX = {name: idx for idx, name in enumerate(_VERBOSITY_LEVELS)}
_DEFAULT_LEVEL = 0  # Level 0 shows only print messages (errors always emit)
_MAX_LEVEL = len(_VERBOSITY_LEVELS) - 1
_COLOR_CODES = {
    "debug": "\033[90m",  # Bright black / gray
    "print": "\033[96m",  # Cyan
    "error": "\033[91m",  # Red
}
_RESET = "\033[0m"


def _initialize_from_environment() -> tuple[bool, int]:
    """Derive initial logging toggle and level from env vars."""
    if _load_env is not None:
        _load_env()

    raw_logging = os.getenv("POLYMARKET_LOGGING")
    if raw_logging is None:
        return True, _DEFAULT_LEVEL

    normalized = raw_logging.strip()
    if normalized.isdigit():
        level_value = int(normalized)
        return True, max(0, level_value)

    return True, _DEFAULT_LEVEL


_enabled, _current_level = _initialize_from_environment()
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
    if isinstance(level, str):
        normalized = level.lower()
        if normalized == "error":
            _current_level = -1  # Only surface errors.
            return
        if normalized not in _VERBOSITY_INDEX:
            raise ValueError(f"Unknown log level: {level}")
        _current_level = _VERBOSITY_INDEX[normalized]
        return

    raise TypeError("Log level must be provided as a string name.")


def get_log_level() -> str:
    """Return current log level name."""
    if _current_level < 0:
        return "error"
    effective_level = min(max(_current_level, 0), _MAX_LEVEL)
    if 0 <= effective_level < len(_VERBOSITY_LEVELS):
        return _VERBOSITY_LEVELS[effective_level]
    return "print"


def _should_emit(level: str) -> bool:
    if level == "error":
        return True  # Always surface errors.
    if not _enabled or _current_level < 0:
        return False
    effective_level = min(max(_current_level, 0), _MAX_LEVEL)
    return _VERBOSITY_INDEX[level] <= effective_level


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


def log_debug(
    *values: Any, sep: str = " ", end: str = "\n", flush: bool = False
) -> None:
    """Emit debug-level diagnostic output."""
    _emit("debug", *values, sep=sep, end=end, flush=flush)


def log_print(
    *values: Any, sep: str = " ", end: str = "\n", flush: bool = False
) -> None:
    """Emit user-facing informational output."""
    _emit("print", *values, sep=sep, end=end, flush=flush)


def log_error(
    *values: Any, sep: str = " ", end: str = "\n", flush: bool = False
) -> None:
    """Emit error output."""
    _emit("error", *values, sep=sep, end=end, flush=flush)


# Backwards compatibility alias.
debug = log_debug
print_log = log_print
error = log_error
log = log_print
