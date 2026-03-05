"""
gateos_manager.telemetry.otlp
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Minimal OTLP/HTTP JSON exporter for Gate-OS traces and logs.

Exports telemetry events in OpenTelemetry Trace/Log Signal format over
HTTP/JSON (OTLP 1.0) without requiring the full opentelemetry-sdk package.

Usage::

    from gateos_manager.telemetry.otlp import OTLPExporter

    exporter = OTLPExporter()
    exporter.export_log("switch.started", {"env": "gaming", "correlation_id": "abc"})
    exporter.export_span("switch.pipeline", start_ns=t0, end_ns=t1, attrs={"env": "gaming"})

    # Or use the module-level singleton
    from gateos_manager.telemetry.otlp import default_exporter
    default_exporter().export_log("foo.bar", {"x": 1})

Environment variables:
    GATEOS_OTLP_ENDPOINT   OTLP collector base URL (default: http://localhost:4318)
    GATEOS_OTLP_SERVICE    Service name in resource (default: gate-os-manager)
    GATEOS_OTLP_TIMEOUT    HTTP request timeout in seconds (default: 3)
    GATEOS_OTLP_DISABLE    Set to '1' to turn off all exports silently
"""
from __future__ import annotations

import json
import os
import sys
import time
import threading
import urllib.error
import urllib.request
import uuid
from typing import Any

from gateos_manager import __version__

# ── Constants ────────────────────────────────────────────────────────────────

_OTLP_LOGS_PATH = "/v1/logs"
_OTLP_TRACES_PATH = "/v1/traces"

_SERVICE_ATTRS = [
    {"key": "service.name", "value": {"stringValue": os.getenv("GATEOS_OTLP_SERVICE", "gate-os-manager")}},
    {"key": "service.version", "value": {"stringValue": __version__}},
    {"key": "telemetry.sdk.name", "value": {"stringValue": "gate-os-otlp"}},
    {"key": "os.type", "value": {"stringValue": sys.platform}},
]


def _to_attr_value(v: Any) -> dict:
    """Convert a Python value to an OTLP AnyValue dict."""
    if isinstance(v, bool):
        return {"boolValue": v}
    if isinstance(v, int):
        return {"intValue": v}
    if isinstance(v, float):
        return {"doubleValue": v}
    return {"stringValue": str(v)}


def _make_attributes(attrs: dict[str, Any]) -> list[dict]:
    return [{"key": k, "value": _to_attr_value(v)} for k, v in attrs.items()]


def _ns_now() -> int:
    return int(time.time() * 1_000_000_000)


def _trace_id() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex[:16]  # 32 hex chars


def _span_id() -> str:
    return uuid.uuid4().hex[:16]  # 16 hex chars


# ── Exporter ─────────────────────────────────────────────────────────────────

class OTLPExporter:
    """Thread-safe OTLP/HTTP JSON exporter."""

    def __init__(
        self,
        endpoint: str | None = None,
        timeout: float | None = None,
    ) -> None:
        base = (endpoint or os.getenv("GATEOS_OTLP_ENDPOINT", "http://localhost:4318")).rstrip("/")
        self._logs_url = base + _OTLP_LOGS_PATH
        self._traces_url = base + _OTLP_TRACES_PATH
        self._timeout = float(timeout or os.getenv("GATEOS_OTLP_TIMEOUT", "3"))
        self._lock = threading.Lock()

    # ── public API ────────────────────────────────────────────────────────────

    def export_log(
        self,
        name: str,
        attrs: dict[str, Any] | None = None,
        severity: str = "INFO",
    ) -> bool:
        """Send a single log record to the OTLP logs endpoint.

        Returns True on success, False on any error (never raises).
        """
        if os.getenv("GATEOS_OTLP_DISABLE") == "1":
            return True

        now = _ns_now()
        payload = {
            "resourceLogs": [
                {
                    "resource": {"attributes": _SERVICE_ATTRS},
                    "scopeLogs": [
                        {
                            "scope": {"name": "gate-os-manager"},
                            "logRecords": [
                                {
                                    "timeUnixNano": str(now),
                                    "observedTimeUnixNano": str(now),
                                    "severityText": severity,
                                    "body": {"stringValue": name},
                                    "attributes": _make_attributes(attrs or {}),
                                    "traceId": _trace_id(),
                                    "spanId": _span_id(),
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        return self._post(self._logs_url, payload)

    def export_span(
        self,
        name: str,
        start_ns: int | None = None,
        end_ns: int | None = None,
        attrs: dict[str, Any] | None = None,
        status_ok: bool = True,
    ) -> bool:
        """Send a single trace span to the OTLP traces endpoint.

        Returns True on success, False on any error (never raises).
        """
        if os.getenv("GATEOS_OTLP_DISABLE") == "1":
            return True

        now = _ns_now()
        start = start_ns or now
        end = end_ns or now
        trace_id = _trace_id()
        span_id = _span_id()

        payload = {
            "resourceSpans": [
                {
                    "resource": {"attributes": _SERVICE_ATTRS},
                    "scopeSpans": [
                        {
                            "scope": {"name": "gate-os-manager"},
                            "spans": [
                                {
                                    "traceId": trace_id,
                                    "spanId": span_id,
                                    "name": name,
                                    "kind": 1,  # SPAN_KIND_INTERNAL
                                    "startTimeUnixNano": str(start),
                                    "endTimeUnixNano": str(end),
                                    "attributes": _make_attributes(attrs or {}),
                                    "status": {
                                        "code": 1 if status_ok else 2,  # OK / ERROR
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        return self._post(self._traces_url, payload)

    def export_batch(self, events: list[dict[str, Any]]) -> bool:
        """Export a batch of log events. Each dict must have at least 'name'.

        Returns True if all events were exported successfully.
        """
        if not events:
            return True
        results = [
            self.export_log(
                e.get("name", "unknown"),
                attrs={k: v for k, v in e.items() if k != "name"},
            )
            for e in events
        ]
        return all(results)

    # ── internals ─────────────────────────────────────────────────────────────

    def _post(self, url: str, payload: dict) -> bool:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"Gate-OS/{__version__} otlp-exporter",
            },
            method="POST",
        )
        try:
            with self._lock:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    resp.read()
            return True
        except (urllib.error.URLError, OSError):
            return False


# ── Module-level singleton (lazy) ─────────────────────────────────────────────

_singleton: OTLPExporter | None = None
_singleton_lock = threading.Lock()


def default_exporter() -> OTLPExporter:
    """Return the module-level singleton OTLPExporter (created on first call)."""
    global _singleton
    if _singleton is None:
        with _singleton_lock:
            if _singleton is None:
                _singleton = OTLPExporter()
    return _singleton
