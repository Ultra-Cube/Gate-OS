"""Structured logging helper with correlation ID support."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

LOG_LEVEL = os.getenv("GATEOS_LOG_LEVEL", "INFO").upper()
LEVEL_ORDER = ["DEBUG", "INFO", "WARN", "ERROR"]


def _enabled(level: str) -> bool:
    try:
        return LEVEL_ORDER.index(level) >= LEVEL_ORDER.index(LOG_LEVEL)
    except ValueError:  # pragma: no cover
        return True


def log(level: str, message: str, correlation_id: str | None = None, **fields: Any) -> None:  # pragma: no cover - IO
    if not _enabled(level):
        return
    record: Dict[str, Any] = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "level": level,
        "msg": message,
        **fields,
    }
    if correlation_id:
        record["correlation_id"] = correlation_id
    try:
        sys.stdout.write(json.dumps(record) + "\n")
    except Exception:  # noqa: BLE001
        pass


def info(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("INFO", message, correlation_id, **fields)


def debug(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("DEBUG", message, correlation_id, **fields)


def warn(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("WARN", message, correlation_id, **fields)


def error(message: str, correlation_id: str | None = None, **fields: Any) -> None:
    log("ERROR", message, correlation_id, **fields)
