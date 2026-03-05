"""Tests for ServiceManager (systemd service orchestration)."""
from __future__ import annotations

import pytest

from gateos_manager.services import ServiceManager, ServiceError


@pytest.fixture
def service_mgr():
    """ServiceManager in dry-run mode (no real systemctl calls)."""
    return ServiceManager(dry_run=True)


def _manifest_with_services(services: list[dict]) -> dict:
    return {
        "apiVersion": "gateos.ultracube.v1alpha1",
        "kind": "Environment",
        "metadata": {"name": "test-env"},
        "spec": {
            "profile": {"category": "dev"},
            "containers": [{"name": "ctr", "image": "example:latest"}],
            "services": services,
        },
    }


def test_start_services_dry_run(service_mgr):
    manifest = _manifest_with_services([
        {"name": "docker", "required": True},
        {"name": "bluetooth", "required": False},
    ])
    started = service_mgr.start_services(manifest)
    assert "docker" in started
    assert "bluetooth" in started


def test_stop_services_dry_run(service_mgr):
    manifest = _manifest_with_services([
        {"name": "docker", "required": True},
    ])
    stopped = service_mgr.stop_services(manifest)
    assert "docker" in stopped


def test_start_empty_services(service_mgr):
    manifest = _manifest_with_services([])
    started = service_mgr.start_services(manifest)
    assert started == []


def test_start_no_services_key(service_mgr):
    """Manifest with no services key should not raise."""
    manifest = {
        "spec": {
            "profile": {"category": "dev"},
            "containers": [],
        }
    }
    started = service_mgr.start_services(manifest)
    assert started == []


def test_service_without_name_is_skipped(service_mgr):
    manifest = _manifest_with_services([{"required": True}])  # no 'name' key
    started = service_mgr.start_services(manifest)
    assert started == []


def test_status_dry_run(service_mgr):
    manifest = _manifest_with_services([{"name": "docker"}])
    status = service_mgr.status(manifest)
    assert "docker" in status
    assert "dry-run" in status["docker"]


def test_required_service_fail_raises(monkeypatch):
    """If a required service fails to start (not dry-run), ServiceError is raised."""
    mgr = ServiceManager(dry_run=False)

    # Patch _systemctl to always fail
    monkeypatch.setattr(mgr, "_systemctl", lambda *a, **kw: False)

    manifest = _manifest_with_services([{"name": "critical-svc", "required": True}])
    with pytest.raises(ServiceError, match="critical-svc"):
        mgr.start_services(manifest)


def test_optional_service_fail_does_not_raise(monkeypatch):
    """If an optional service fails, no exception — just not in started list."""
    mgr = ServiceManager(dry_run=False)
    monkeypatch.setattr(mgr, "_systemctl", lambda *a, **kw: False)

    manifest = _manifest_with_services([{"name": "optional-svc", "required": False}])
    started = mgr.start_services(manifest)
    assert "optional-svc" not in started
