"""Tests for Phase 6 — Performance & Observability.

Covers:
- Prometheus registry (Counter, Gauge, Histogram) correctness
- Text exposition format validity
- /metrics FastAPI endpoint
- API request counter middleware
- Switch latency tracking helpers
- Perf CI threshold: switch pipeline must complete in < 3 s
"""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ──────────────────────────────────────────────────────────────────────────
# Registry unit tests
# ──────────────────────────────────────────────────────────────────────────

def test_counter_increments():
    from gateos_manager.telemetry.prometheus import Counter
    c = Counter()
    assert c.value == 0.0
    c.inc()
    assert c.value == 1.0
    c.inc(4.5)
    assert c.value == 5.5


def test_gauge_set():
    from gateos_manager.telemetry.prometheus import Gauge
    g = Gauge()
    g.set(3.14)
    assert g.value == pytest.approx(3.14)
    g.set(0.0)
    assert g.value == 0.0


def test_histogram_observe_and_p99():
    from gateos_manager.telemetry.prometheus import Histogram
    h = Histogram()
    for i in range(1, 101):
        h.observe(float(i))
    assert h.count == 100
    assert h.sum == pytest.approx(5050.0)
    p99 = h.p99()
    assert 98 <= p99 <= 100


def test_histogram_empty_p99():
    from gateos_manager.telemetry.prometheus import Histogram
    h = Histogram()
    assert h.p99() == 0.0


def test_histogram_rolling_window_capped_at_100():
    from gateos_manager.telemetry.prometheus import Histogram
    h = Histogram()
    for i in range(200):
        h.observe(float(i))
    assert h.count == 200          # total count unbounded
    assert len(h._window) == 100   # window capped


# ──────────────────────────────────────────────────────────────────────────
# MetricsRegistry tests
# ──────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def fresh_registry():
    from gateos_manager.telemetry.prometheus import MetricsRegistry
    return MetricsRegistry()


def test_registry_inc_and_set(fresh_registry):
    r = fresh_registry
    r.inc("gateos_switch_total", labels={"env": "gaming", "status": "ok"})
    r.inc("gateos_switch_total", labels={"env": "gaming", "status": "ok"})
    r.set("gateos_switch_latency_seconds", 1.5, labels={"env": "gaming"})

    text = r.text_exposition()
    assert 'env="gaming"' in text and 'status="ok"' in text
    assert 'gateos_switch_latency_seconds' in text and '1.5' in text


def test_registry_observe(fresh_registry):
    r = fresh_registry
    r.observe("gateos_switch_latency_hist", 0.8, labels={"env": "dev"})
    r.observe("gateos_switch_latency_hist", 1.2, labels={"env": "dev"})

    text = r.text_exposition()
    assert "gateos_switch_latency_hist_count" in text
    assert "gateos_switch_latency_hist_sum" in text


def test_registry_text_format_has_help_and_type(fresh_registry):
    r = fresh_registry
    r.inc("gateos_api_requests_total", labels={"method": "GET", "path": "/metrics", "status_code": "200"})
    text = r.text_exposition()
    assert "# HELP gateos_api_requests_total" in text
    assert "# TYPE gateos_api_requests_total" in text


def test_registry_build_info_gauge(fresh_registry):
    text = fresh_registry.text_exposition()
    assert "gateos_build_info" in text
    assert 'version="' in text


def test_registry_no_labels(fresh_registry):
    r = fresh_registry
    r.set("gateos_active_environment", 1.0, labels={"env": "gaming"})
    text = r.text_exposition()
    assert "gateos_active_environment" in text


def test_registry_multiple_label_sets(fresh_registry):
    r = fresh_registry
    r.inc("gateos_switch_total", labels={"env": "gaming", "status": "ok"})
    r.inc("gateos_switch_total", labels={"env": "dev", "status": "error"})
    text = r.text_exposition()
    assert 'env="gaming"' in text
    assert 'env="dev"' in text


# ──────────────────────────────────────────────────────────────────────────
# FastAPI /metrics endpoint
# ──────────────────────────────────────────────────────────────────────────

try:
    from fastapi.testclient import TestClient
    from gateos_manager.api.server import app
    _API_AVAILABLE = True
except ImportError:
    _API_AVAILABLE = False

pytestmark_api = pytest.mark.skipif(not _API_AVAILABLE, reason="FastAPI not installed")


@pytest.fixture()
def api_client():
    from fastapi.testclient import TestClient
    from gateos_manager.api.server import app
    return TestClient(app, raise_server_exceptions=False)


@pytestmark_api
def test_metrics_endpoint_returns_200(api_client):
    resp = api_client.get("/metrics")
    assert resp.status_code == 200


@pytestmark_api
def test_metrics_endpoint_content_type(api_client):
    resp = api_client.get("/metrics")
    assert "text/plain" in resp.headers["content-type"]


@pytestmark_api
def test_metrics_endpoint_contains_build_info(api_client):
    resp = api_client.get("/metrics")
    assert "gateos_build_info" in resp.text


@pytestmark_api
def test_metrics_middleware_increments_counter(api_client):
    # Hit /health or /environments (unauthenticated) to trigger middleware
    api_client.get("/environments")
    resp = api_client.get("/metrics")
    assert "gateos_api_requests_total" in resp.text


# ──────────────────────────────────────────────────────────────────────────
# Perf CI threshold: switch pipeline < 3 s
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.benchmark
def test_switch_pipeline_completes_under_3_seconds(tmp_path):
    """CI perf guard: the full switch pipeline must complete in < 3 s.

    We call the orchestrator with a real manifest but mocked sub-systems
    (ServiceManager, ContainerManager, ProfileApplicator) so the test
    measures Python overhead only, not actual systemd/podman latency.
    """
    from unittest.mock import patch, MagicMock
    from gateos_manager.switch.orchestrator import switch_environment

    schema = Path("docs/architecture/schemas/environment-manifest.schema.yaml")
    if not schema.exists():
        pytest.skip("Schema not available in this environment")

    example = Path("examples/environments")
    if not example.exists() or not list(example.glob("*.yaml")):
        pytest.skip("No example manifests available")

    target_env = next(iter(example.glob("*.yaml")))
    import yaml
    manifest_data = yaml.safe_load(target_env.read_text())
    env_name = manifest_data.get("metadata", {}).get("name", "")
    if not env_name:
        pytest.skip("Could not determine env name from manifest")

    mock_sm = MagicMock()
    mock_cm = MagicMock()
    mock_cm.start_container.return_value = "mock-container-id"
    mock_pa = MagicMock()

    start = time.monotonic()
    with patch("gateos_manager.switch.orchestrator.ServiceManager", return_value=mock_sm), \
         patch("gateos_manager.switch.orchestrator.ContainerManager", return_value=mock_cm), \
         patch("gateos_manager.switch.orchestrator.ProfileApplicator", return_value=mock_pa):
        result = switch_environment(env_name, schema)
    elapsed = time.monotonic() - start

    assert elapsed < 3.0, f"Switch pipeline took {elapsed:.2f}s — exceeds 3s CI threshold"
    assert result.get("status") in ("ok", "success", "error", "rolled_back")  # completed


# ──────────────────────────────────────────────────────────────────────────
# Metrics server start/stop
# ──────────────────────────────────────────────────────────────────────────

def test_start_metrics_server_returns_port():
    from gateos_manager.telemetry.prometheus import start_metrics_server, stop_metrics_server
    try:
        port = start_metrics_server(port=19091)
        assert port == 19091
        # Second call returns same port (idempotent)
        port2 = start_metrics_server(port=19091)
        assert port2 == 19091
    finally:
        stop_metrics_server()


def test_metrics_server_serves_metrics():
    import urllib.request
    from gateos_manager.telemetry.prometheus import start_metrics_server, stop_metrics_server, registry
    try:
        start_metrics_server(port=19092)
        time.sleep(0.05)  # brief startup
        with urllib.request.urlopen("http://127.0.0.1:19092/metrics", timeout=2) as resp:
            body = resp.read().decode()
        assert "gateos_build_info" in body
    finally:
        stop_metrics_server()


def test_metrics_server_404_on_unknown_path():
    import urllib.request, urllib.error
    from gateos_manager.telemetry.prometheus import start_metrics_server, stop_metrics_server
    try:
        start_metrics_server(port=19093)
        time.sleep(0.05)
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen("http://127.0.0.1:19093/unknown", timeout=2)
        assert exc_info.value.code == 404
    finally:
        stop_metrics_server()
