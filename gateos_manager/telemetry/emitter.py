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
import urllib.request
import urllib.error
import threading
import queue
import atexit

# Simple batch queue (not multi-process safe)
_BATCH_Q: 'queue.Queue[dict]' | None = None
_BATCH_LOCK = threading.Lock()
_FLUSH_THREAD: threading.Thread | None = None


def _ensure_batch_thread():  # pragma: no cover - thread mgmt
    global _BATCH_Q, _FLUSH_THREAD
    if os.getenv('GATEOS_TELEMETRY_BATCH') != '1':
        return
    with _BATCH_LOCK:
        if _BATCH_Q is None:
            _BATCH_Q = queue.Queue(maxsize=1000)
        if _FLUSH_THREAD is None or not _FLUSH_THREAD.is_alive():
            _FLUSH_THREAD = threading.Thread(target=_flush_loop, daemon=True)
            _FLUSH_THREAD.start()


def _flush_loop():  # pragma: no cover - background
    interval = float(os.getenv('GATEOS_TELEMETRY_BATCH_INTERVAL', '2'))
    max_batch = int(os.getenv('GATEOS_TELEMETRY_BATCH_SIZE', '50'))
    while True:
        try:
            if _BATCH_Q is None:
                return
            first = _BATCH_Q.get()
            batch = [first]
            try:
                while len(batch) < max_batch:
                    batch.append(_BATCH_Q.get_nowait())
            except queue.Empty:
                pass
            _export_batch(batch)
        except Exception:
            pass
        finally:
            # sleep after batch to accumulate more events
            import time as _t
            _t.sleep(interval)


def _export_batch(batch: list[dict]):  # pragma: no cover - IO
    otlp_endpoint = os.getenv("GATEOS_TELEMETRY_OTLP_HTTP")
    if not otlp_endpoint:
        return
    try:
        req = urllib.request.Request(otlp_endpoint, data=json.dumps(batch).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=1.2)
    except Exception:
        pass


def flush() -> None:  # pragma: no cover - flush logic
    """Flush any queued batched telemetry events synchronously.

    Called automatically at process exit, safe to invoke manually.
    Only affects OTLP batch queue; file/stdout already written eagerly.
    """
    if os.getenv('GATEOS_TELEMETRY_BATCH') != '1':
        return
    global _BATCH_Q
    if _BATCH_Q is None:
        return
    pending: list[dict] = []
    try:
        while True:
            pending.append(_BATCH_Q.get_nowait())
    except Exception:
        pass
    if pending:
        _export_batch(pending)


def _register_flush():  # pragma: no cover
    try:
        atexit.register(flush)
    except Exception:
        pass


def _target() -> Optional[str]:  # pragma: no cover - simple
    return os.getenv("GATEOS_TELEMETRY_FILE")


def emit(event_type: str, correlation_id: str | None = None, **fields: Any) -> None:  # pragma: no cover - IO heavy
    if os.getenv("GATEOS_TELEMETRY_ENABLED") != "1":
        return
    payload: Dict[str, Any] = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "event": event_type,
        **fields,
    }
    if correlation_id:
        payload["correlation_id"] = correlation_id
    # initialize batching if requested
    _ensure_batch_thread()
    _register_flush()

    # stdout / file sink (always immediate)
    line = json.dumps(payload) + "\n"
    target = _target()
    try:
        if target:
            with open(target, "a", encoding="utf-8") as f:
                f.write(line)
        else:
            sys.stdout.write(line)
    except Exception:
        pass
    # optional OTLP HTTP export (very lightweight, no batching)
    otlp_endpoint = os.getenv("GATEOS_TELEMETRY_OTLP_HTTP")
    if otlp_endpoint:
        if os.getenv('GATEOS_TELEMETRY_BATCH') == '1' and _BATCH_Q is not None:
            try:
                _BATCH_Q.put_nowait(payload)
            except Exception:
                pass
        else:
            try:
                req = urllib.request.Request(otlp_endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                urllib.request.urlopen(req, timeout=0.8)  # nosec B310 - controlled by env
            except Exception:
                pass
