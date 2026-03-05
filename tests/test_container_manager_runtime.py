"""Extended tests for ContainerManager — runtime (non-dry-run) paths.

Covers lines previously uncovered:
  - _detect_runtime() when shutil.which returns None → dry-run fallback
  - _detect_runtime() when podman found
  - _start_single() runtime path: success, non-zero returncode, TimeoutExpired, generic exception
  - _stop_single() runtime path: success, bad returncode (warns but continues), TimeoutExpired, generic exception
  - start() skip already-running container
  - stop() skip not-running container
  - _start_single() skip when no image
  - Top-level mounts + readOnly flag applied to cmd
  - Per-container mounts with readOnly flag
  - spec.command parsed via shlex
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from gateos_manager.containers.manager import ContainerManager


# ─────────────────────────────────────────────────────────────────────────────
# _detect_runtime()
# ─────────────────────────────────────────────────────────────────────────────

def test_detect_runtime_podman_found(monkeypatch):
    monkeypatch.delenv("GATEOS_CONTAINER_DRY_RUN", raising=False)
    monkeypatch.delenv("GATEOS_CONTAINER_RUNTIME", raising=False)
    with patch("gateos_manager.containers.manager.shutil.which", side_effect=lambda x: "/usr/bin/podman" if x == "podman" else None):
        mgr = ContainerManager(dry_run=None, runtime=None)
    assert mgr._runtime == "podman"
    assert mgr._dry_run is False


def test_detect_runtime_docker_fallback(monkeypatch):
    monkeypatch.delenv("GATEOS_CONTAINER_DRY_RUN", raising=False)
    monkeypatch.delenv("GATEOS_CONTAINER_RUNTIME", raising=False)
    with patch("gateos_manager.containers.manager.shutil.which", side_effect=lambda x: "/usr/bin/docker" if x == "docker" else None):
        mgr = ContainerManager(dry_run=None, runtime=None)
    assert mgr._runtime == "docker"


def test_detect_runtime_none_switches_dry_run(monkeypatch):
    monkeypatch.delenv("GATEOS_CONTAINER_DRY_RUN", raising=False)
    monkeypatch.delenv("GATEOS_CONTAINER_RUNTIME", raising=False)
    with patch("gateos_manager.containers.manager.shutil.which", return_value=None):
        mgr = ContainerManager(dry_run=None, runtime=None)
    assert mgr._dry_run is True
    assert mgr._runtime == "none"


# ─────────────────────────────────────────────────────────────────────────────
# _start_single() — runtime path
# ─────────────────────────────────────────────────────────────────────────────

def _make_mgr() -> ContainerManager:
    """Real runtime manager with dummy binary to skip _detect_runtime."""
    return ContainerManager(dry_run=False, runtime="podman")


def test_start_single_runtime_success():
    mgr = _make_mgr()
    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        ok = mgr._start_single("c1", {"image": "redis:7"}, manifest_name="dev")

    assert ok is True
    assert mgr._state["c1"] == "running"
    cmd_used = mock_run.call_args[0][0]
    assert "podman" in cmd_used
    assert "redis:7" in cmd_used
    assert "--label" in cmd_used


def test_start_single_runtime_nonzero_returncode():
    mgr = _make_mgr()
    mock_result = MagicMock()
    mock_result.returncode = 125
    mock_result.stderr = b"image not found"

    with patch("subprocess.run", return_value=mock_result):
        ok = mgr._start_single("c1", {"image": "bad:image"}, manifest_name="dev")

    assert ok is False
    assert mgr._state.get("c1") != "running"


def test_start_single_runtime_timeout():
    mgr = _make_mgr()

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="podman", timeout=30)):
        ok = mgr._start_single("c1", {"image": "slow:image"}, manifest_name="dev")

    assert ok is False


def test_start_single_runtime_generic_exception():
    mgr = _make_mgr()

    with patch("subprocess.run", side_effect=OSError("socket error")):
        ok = mgr._start_single("c1", {"image": "any:image"}, manifest_name="dev")

    assert ok is False


def test_start_single_no_image_skipped():
    mgr = _make_mgr()
    ok = mgr._start_single("c1", {}, manifest_name="dev")
    assert ok is False


def test_start_single_applies_env_vars():
    mgr = _make_mgr()
    mock_result = MagicMock(returncode=0)
    spec = {"image": "myapp:1", "env": {"DEBUG": "true", "PORT": "8080"}}

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        mgr._start_single("c1", spec, manifest_name="dev")

    cmd = mock_run.call_args[0][0]
    assert "-e" in cmd
    assert "DEBUG=true" in cmd
    assert "PORT=8080" in cmd


def test_start_single_applies_ports():
    mgr = _make_mgr()
    mock_result = MagicMock(returncode=0)
    spec = {"image": "nginx:alpine", "ports": ["80:80", "443:443"]}

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        mgr._start_single("c1", spec, manifest_name="dev")

    cmd = mock_run.call_args[0][0]
    assert "-p" in cmd
    assert "80:80" in cmd
    assert "443:443" in cmd


def test_start_single_top_mounts_applied():
    mgr = _make_mgr()
    mock_result = MagicMock(returncode=0)
    top_mounts = [{"source": "/host/data", "target": "/data", "readOnly": False}]

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        mgr._start_single("c1", {"image": "alpine"}, manifest_name="dev", top_mounts=top_mounts)

    cmd = mock_run.call_args[0][0]
    assert "/host/data:/data" in cmd


def test_start_single_top_mounts_readonly():
    mgr = _make_mgr()
    mock_result = MagicMock(returncode=0)
    top_mounts = [{"source": "/etc/config", "target": "/config", "readOnly": True}]

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        mgr._start_single("c1", {"image": "alpine"}, manifest_name="dev", top_mounts=top_mounts)

    cmd = mock_run.call_args[0][0]
    assert "/etc/config:/config:ro" in cmd


def test_start_single_per_container_mounts():
    mgr = _make_mgr()
    mock_result = MagicMock(returncode=0)
    spec = {
        "image": "myapp:1",
        "mounts": [{"source": "/var/run/docker.sock", "target": "/var/run/docker.sock", "readOnly": False}],
    }

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        mgr._start_single("c1", spec, manifest_name="dev")

    cmd = mock_run.call_args[0][0]
    assert "/var/run/docker.sock:/var/run/docker.sock" in cmd


def test_start_single_command_shlex_split():
    mgr = _make_mgr()
    mock_result = MagicMock(returncode=0)
    spec = {"image": "busybox", "command": "sleep 300"}

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        mgr._start_single("c1", spec, manifest_name="dev")

    cmd = mock_run.call_args[0][0]
    assert "sleep" in cmd
    assert "300" in cmd


# ─────────────────────────────────────────────────────────────────────────────
# _stop_single() — runtime path
# ─────────────────────────────────────────────────────────────────────────────

def test_stop_single_runtime_success():
    mgr = _make_mgr()
    mgr._state["c1"] = "running"
    mock_result = MagicMock(returncode=0)

    with patch("subprocess.run", return_value=mock_result):
        ok = mgr._stop_single("c1")

    assert ok is True
    assert mgr._state["c1"] == "stopped"


def test_stop_single_nonzero_warns_but_proceeds():
    """Non-zero stop returncode should warn but still attempt rm and return True."""
    mgr = _make_mgr()
    mgr._state["c1"] = "running"
    # First call (stop) returns non-zero; second call (rm) returns 0
    results = [MagicMock(returncode=1, stderr=b"no such container"), MagicMock(returncode=0)]

    with patch("subprocess.run", side_effect=results):
        ok = mgr._stop_single("c1")

    assert ok is True
    assert mgr._state["c1"] == "stopped"


def test_stop_single_timeout():
    mgr = _make_mgr()
    mgr._state["c1"] = "running"

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="podman", timeout=15)):
        ok = mgr._stop_single("c1")

    assert ok is False


def test_stop_single_generic_exception():
    mgr = _make_mgr()
    mgr._state["c1"] = "running"

    with patch("subprocess.run", side_effect=RuntimeError("kernel panic")):
        ok = mgr._stop_single("c1")

    assert ok is False


# ─────────────────────────────────────────────────────────────────────────────
# start() / stop() public API edge cases
# ─────────────────────────────────────────────────────────────────────────────

def test_start_skips_already_running():
    mgr = ContainerManager(dry_run=True, runtime="podman")
    manifest = {"name": "dev", "containers": [{"name": "redis", "image": "redis:7"}]}
    mgr.start(manifest)
    # Second start should return empty (already running)
    started = mgr.start(manifest)
    assert started == []


def test_stop_skips_not_running():
    mgr = ContainerManager(dry_run=True, runtime="podman")
    manifest = {"name": "dev", "containers": [{"name": "redis", "image": "redis:7"}]}
    # Never started
    stopped = mgr.stop(manifest)
    assert stopped == []


def test_start_empty_containers():
    mgr = ContainerManager(dry_run=True)
    started = mgr.start({"containers": []})
    assert started == []


def test_status_unknown_for_never_started():
    mgr = ContainerManager(dry_run=True)
    manifest = {"name": "x", "containers": [{"name": "a", "image": "img"}]}
    s = mgr.status(manifest)
    assert s["gateos_x_a"] == "unknown"


def test_container_name_uses_image_when_no_name():
    mgr = ContainerManager(dry_run=True)
    manifest = {"name": "test", "containers": [{"image": "nginx:alpine"}]}
    started = mgr.start(manifest)
    assert len(started) == 1
    assert "nginx:alpine" in started[0]
