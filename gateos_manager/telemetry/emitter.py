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
from typing import Any, Dict


def emit(event_type: str, **fields: Any) -> None:  # pragma: no cover - trivial IO
    if os.getenv("GATEOS_TELEMETRY_ENABLED") != "1":
        return
    payload: Dict[str, Any] = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "event": event_type,
        **fields,
    }
    try:
        sys.stdout.write(json.dumps(payload) + "\n")
    except Exception:  # noqa: BLE001
        pass
