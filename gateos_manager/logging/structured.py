"""Structured logging helper with correlation ID support."""
from __future__ import annotations

import json
import os
import sys
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

LEVEL_ORDER = ["DEBUG", "INFO", "WARN", "ERROR"]


def _current_level() -> str:
    return os.getenv("GATEOS_LOG_LEVEL", "INFO").upper()


def _enabled(level: str) -> bool:
    try:
        return LEVEL_ORDER.index(level) >= LEVEL_ORDER.index(_current_level())
    except ValueError:  # pragma: no cover
        return True


def log(level: str, message: str, correlation_id: str | None = None, **fields: Any) -> None:  # pragma: no cover - IO
    if not _enabled(level):
        return
    record: dict[str, Any] = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "level": level,
        "msg": message,
        **fields,
    }
    if correlation_id:
        record["correlation_id"] = correlation_id
    with suppress(Exception):  # noqa: BLE001
        sys.stdout.write(json.dumps(record) + "\n")


def info(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("INFO", message, correlation_id, **fields)


def debug(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("DEBUG", message, correlation_id, **fields)


def warn(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("WARN", message, correlation_id, **fields)


def error(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("ERROR", message, correlation_id, **fields)
