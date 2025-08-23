"""Telemetry event emitter skeleton.

Future implementation will support pluggable backends (stdout, file, OTLP).
For now we just provide a simple synchronous emit() that prints structured JSON
to stdout when GATEOS_TELEMETRY_ENABLED=1.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _target() -> Optional[str]:  # pragma: no cover - simple
    return os.getenv("GATEOS_TELEMETRY_FILE")


def emit(event_type: str, correlation_id: str | None = None, **fields: Any) -> None:  # pragma: no cover - IO
    if os.getenv("GATEOS_TELEMETRY_ENABLED") != "1":
        return
    payload: Dict[str, Any] = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "event": event_type,
        **fields,
    }
    if correlation_id:
        payload["correlation_id"] = correlation_id
    line = json.dumps(payload) + "\n"
    target = _target()
    try:
        if target:
            with open(target, "a", encoding="utf-8") as f:
                f.write(line)
        else:
            sys.stdout.write(line)
    except Exception:  # noqa: BLE001
        pass
