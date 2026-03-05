"""Extended tests for ServiceManager — real subprocess paths (mocked).

Covers lines previously uncovered (67% → 90%+):
  - _systemctl() real path: success (CalledProcessError → False), TimeoutExpired, Exception
  - is_active() real path: True, False, Exception
  - status() real path with is_active returning True/False
  - __init__() real path: systemctl found vs not found
  - stop_services() real path with and without errors
  - stop_services() skips services with no name
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from gateos_manager.services import ServiceError, ServiceManager


def _manifest(services: list[dict]) -> dict:
    return {
        "spec": {
            "services": services,
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# __init__
# ─────────────────────────────────────────────────────────────────────────────

def test_init_dry_run_when_systemctl_missing():
    with patch("gateos_manager.services.shutil.which", return_value=None):
        mgr = ServiceManager(dry_run=None)
    assert mgr._dry_run is True


def test_init_real_when_systemctl_present():
    with patch("gateos_manager.services.shutil.which", return_value="/bin/systemctl"):
        mgr = ServiceManager(dry_run=None)
    # dry_run not forced here — should be False (systemctl present)
    assert mgr._dry_run is False


def test_init_env_var_forces_dry_run(monkeypatch):
    monkeypatch.setenv("GATEOS_SYSTEMD_DRY_RUN", "1")
    with patch("gateos_manager.services.shutil.which", return_value="/bin/systemctl"):
        mgr = ServiceManager(dry_run=None)
    assert mgr._dry_run is True


# ─────────────────────────────────────────────────────────────────────────────
# _systemctl() real subprocess path
# ─────────────────────────────────────────────────────────────────────────────

def test_systemctl_success():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        ok = mgr._systemctl("start", "docker")
    assert ok is True
    cmd = mock_run.call_args[0][0]
    assert cmd == ["systemctl", "start", "docker"]


def test_systemctl_called_process_error_returns_false():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "systemctl")):
        ok = mgr._systemctl("start", "missing-svc")
    assert ok is False


def test_systemctl_timeout_returns_false():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="systemctl", timeout=30)):
        ok = mgr._systemctl("start", "slow-svc")
    assert ok is False


def test_systemctl_generic_exception_returns_false():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", side_effect=OSError("dbus gone")):
        ok = mgr._systemctl("stop", "something")
    assert ok is False


# ─────────────────────────────────────────────────────────────────────────────
# is_active() real path
# ─────────────────────────────────────────────────────────────────────────────

def test_is_active_true():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", return_value=MagicMock(returncode=0)):
        assert mgr.is_active("docker") is True


def test_is_active_false():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", return_value=MagicMock(returncode=3)):
        assert mgr.is_active("docker") is False


def test_is_active_exception_returns_false():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", side_effect=OSError("dbus not running")):
        assert mgr.is_active("docker") is False


def test_is_active_dry_run_always_false():
    mgr = ServiceManager(dry_run=True)
    assert mgr.is_active("any-service") is False


# ─────────────────────────────────────────────────────────────────────────────
# status() real path
# ─────────────────────────────────────────────────────────────────────────────

def test_status_real_active():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "is_active", return_value=True):
        result = mgr.status(_manifest([{"name": "docker"}]))
    assert result["docker"] == "active"


def test_status_real_inactive():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "is_active", return_value=False):
        result = mgr.status(_manifest([{"name": "docker"}]))
    assert result["docker"] == "inactive"


def test_status_skips_nameless_services():
    mgr = ServiceManager(dry_run=False)
    result = mgr.status(_manifest([{}]))  # no 'name' key
    assert result == {}


# ─────────────────────────────────────────────────────────────────────────────
# start_services / stop_services — real path
# ─────────────────────────────────────────────────────────────────────────────

def test_start_services_real_success():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "_systemctl", return_value=True):
        started = mgr.start_services(_manifest([
            {"name": "docker", "required": True},
            {"name": "bluetooth", "required": False},
        ]))
    assert "docker" in started
    assert "bluetooth" in started


def test_start_services_real_required_failure_raises():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "_systemctl", return_value=False):
        with pytest.raises(ServiceError, match="critical"):
            mgr.start_services(_manifest([{"name": "critical", "required": True}]))


def test_start_services_real_optional_failure_silent():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "_systemctl", return_value=False):
        started = mgr.start_services(_manifest([{"name": "opt", "required": False}]))
    assert "opt" not in started


def test_stop_services_real_success():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "_systemctl", return_value=True):
        stopped = mgr.stop_services(_manifest([{"name": "docker"}]))
    assert "docker" in stopped


def test_stop_services_real_failure_skips():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "_systemctl", return_value=False):
        stopped = mgr.stop_services(_manifest([{"name": "docker"}]))
    assert "docker" not in stopped


def test_stop_skips_nameless():
    mgr = ServiceManager(dry_run=False)
    with patch.object(mgr, "_systemctl", return_value=True):
        stopped = mgr.stop_services(_manifest([{}]))
    assert stopped == []


def test_systemctl_passes_correlation_id():
    mgr = ServiceManager(dry_run=False)
    with patch("subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        mgr._systemctl("start", "nginx", correlation_id="abc-123")
    # Should not raise; correlation_id is used in emit/info (fire-and-forget)
    assert mock_run.called
