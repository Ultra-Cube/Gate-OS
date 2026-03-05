"""
gateos_manager.telemetry.prometheus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Prometheus metrics endpoint for Gate-OS.

Exposes a ``/metrics`` HTTP endpoint (text/plain; version=0.0.4) that the
Prometheus scraper can consume.  The endpoint is served by a lightweight
``http.server.BaseHTTPRequestHandler`` running in a daemon thread so it never
blocks the main application.

Metrics exported:
    gateos_switch_total{env, status}          counter   Total environment switches
    gateos_switch_latency_seconds{env}        gauge     Latest switch duration (s)
    gateos_switch_latency_p99_seconds{env}    gauge     Rolling P99 over last 100 switches
    gateos_active_environment{env}            gauge     1 = currently active, 0 = inactive
    gateos_api_requests_total{method,path,status_code}  counter
    gateos_memory_delta_bytes{env}            gauge     RSS memory delta after last switch
    gateos_build_info{version,python}         gauge     Always 1; carries version labels

Usage::

    from gateos_manager.telemetry.prometheus import registry, start_metrics_server

    # Increment a counter
    registry.inc("gateos_switch_total", labels={"env": "gaming", "status": "ok"})

    # Record a latency sample
    registry.set("gateos_switch_latency_seconds", value=1.24, labels={"env": "gaming"})

    # Start HTTP server on port 9090
    start_metrics_server(port=9090)
"""
from __future__ import annotations

import collections
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from gateos_manager import __version__

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_MetricKey = tuple[str, tuple[tuple[str, str], ...]]  # (name, sorted_labels)


class Counter:
    """A monotonically increasing counter."""
    __slots__ = ("_v", "_lock")

    def __init__(self) -> None:
        self._v: float = 0.0
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._v += amount

    @property
    def value(self) -> float:
        return self._v


class Gauge:
    """A gauge that can go up and down."""
    __slots__ = ("_v", "_lock")

    def __init__(self, initial: float = 0.0) -> None:
        self._v: float = initial
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._v = value

    @property
    def value(self) -> float:
        return self._v


class Histogram:
    """A minimal histogram that tracks count, sum, and a rolling window for P99."""
    __slots__ = ("_count", "_sum", "_window", "_lock")
    _WINDOW_SIZE = 100

    def __init__(self) -> None:
        self._count: int = 0
        self._sum: float = 0.0
        self._window: collections.deque[float] = collections.deque(maxlen=self._WINDOW_SIZE)
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._count += 1
            self._sum += value
            self._window.append(value)

    @property
    def count(self) -> int:
        return self._count

    @property
    def sum(self) -> float:
        return self._sum

    def p99(self) -> float:
        with self._lock:
            if not self._window:
                return 0.0
            sorted_w = sorted(self._window)
            idx = max(0, int(len(sorted_w) * 0.99) - 1)
            return sorted_w[idx]


class MetricsRegistry:
    """Thread-safe metrics registry."""

    def __init__(self) -> None:
        self._counters: dict[_MetricKey, Counter] = {}
        self._gauges: dict[_MetricKey, Gauge] = {}
        self._histograms: dict[_MetricKey, Histogram] = {}
        self._meta: dict[str, tuple[str, str]] = {}  # name → (type, help)
        self._lock = threading.Lock()

        # Pre-declare metrics
        self._declare("gateos_switch_total", "counter", "Total environment switches")
        self._declare("gateos_switch_latency_seconds", "gauge", "Latest switch latency (s)")
        self._declare("gateos_switch_latency_p99_seconds", "gauge", "P99 latency over last 100 switches")
        self._declare("gateos_switch_latency_hist", "histogram", "Switch latency histogram")
        self._declare("gateos_active_environment", "gauge", "1 = currently active environment")
        self._declare("gateos_api_requests_total", "counter", "Total API HTTP requests")
        self._declare("gateos_memory_delta_bytes", "gauge", "RSS memory delta after last switch (bytes)")
        self._declare("gateos_build_info", "gauge", "Gate-OS build metadata")

        # Build-info gauge (always 1)
        import sys as _sys
        self.set("gateos_build_info", 1.0, labels={
            "version": __version__,
            "python": _sys.version.split()[0],
        })

    def _declare(self, name: str, kind: str, help_text: str) -> None:
        self._meta[name] = (kind, help_text)

    def _key(self, name: str, labels: dict[str, str]) -> _MetricKey:
        return (name, tuple(sorted(labels.items())))

    # ── Write ──────────────────────────────────────────────────────────────

    def inc(self, name: str, amount: float = 1.0, *, labels: dict[str, str] | None = None) -> None:
        labels = labels or {}
        key = self._key(name, labels)
        with self._lock:
            if key not in self._counters:
                self._counters[key] = Counter()
            self._counters[key].inc(amount)

    def set(self, name: str, value: float, *, labels: dict[str, str] | None = None) -> None:
        labels = labels or {}
        key = self._key(name, labels)
        with self._lock:
            if key not in self._gauges:
                self._gauges[key] = Gauge()
            self._gauges[key].set(value)

    def observe(self, name: str, value: float, *, labels: dict[str, str] | None = None) -> None:
        labels = labels or {}
        key = self._key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = Histogram()
            self._histograms[key].observe(value)

    # ── Read (Prometheus text format) ──────────────────────────────────────

    def text_exposition(self) -> str:
        lines: list[str] = []

        def label_str(lmap: tuple[tuple[str, str], ...]) -> str:
            if not lmap:
                return ""
            parts = ", ".join(f'{k}="{v}"' for k, v in lmap)
            return "{" + parts + "}"

        with self._lock:
            for (name, lmap), c in self._counters.items():
                kind, help_text = self._meta.get(name, ("counter", ""))
                lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} {kind}")
                lines.append(f"{name}{label_str(lmap)} {c.value}")

            for (name, lmap), g in self._gauges.items():
                kind, help_text = self._meta.get(name, ("gauge", ""))
                lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} {kind}")
                lines.append(f"{name}{label_str(lmap)} {g.value}")

            for (name, lmap), h in self._histograms.items():
                kind, help_text = self._meta.get(name, ("histogram", ""))
                lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} {kind}")
                lines.append(f"{name}_count{label_str(lmap)} {h.count}")
                lines.append(f"{name}_sum{label_str(lmap)} {h.sum}")

        return "\n".join(lines) + "\n"


# Module-level singleton
registry = MetricsRegistry()

# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

_server_instance: HTTPServer | None = None
_server_lock = threading.Lock()


class _MetricsHandler(BaseHTTPRequestHandler):
    log_message = lambda self, *a, **kw: None  # silence access log

    def do_GET(self) -> None:
        if self.path not in ("/metrics", "/metrics/"):
            self.send_response(404)
            self.end_headers()
            return
        body = registry.text_exposition().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_metrics_server(
    port: int | None = None,
    host: str = "127.0.0.1",
) -> int:
    """Start the Prometheus metrics HTTP server in a daemon thread.

    Returns the port the server is listening on.
    If the server is already running, returns the existing port.
    """
    global _server_instance

    port = port or int(os.getenv("GATEOS_METRICS_PORT", "9090"))

    with _server_lock:
        if _server_instance is not None:
            return _server_instance.server_address[1]

        server = HTTPServer((host, port), _MetricsHandler)
        _server_instance = server

    t = threading.Thread(target=server.serve_forever, daemon=True, name="gateos-metrics")
    t.start()
    return port


def stop_metrics_server() -> None:
    """Shut down the metrics server (mainly for tests)."""
    global _server_instance
    with _server_lock:
        if _server_instance is not None:
            _server_instance.shutdown()
            _server_instance = None
