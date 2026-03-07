"""Tests for ProfileApplicator (CPU governor, GPU mode, NIC priority)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from gateos_manager.profile import ProfileApplicator


@pytest.fixture
def applicator():
    return ProfileApplicator(dry_run=True)


def _manifest_with_performance(perf: dict) -> dict:
    return {
        "spec": {
            "profile": {
                "category": "gaming",
                "performance": perf,
            },
            "containers": [],
        }
    }


def test_apply_cpu_governor_dry_run(applicator):
    manifest = _manifest_with_performance({"cpuGovernor": "performance"})
    result = applicator.apply(manifest)
    assert "cpuGovernor" in result
    assert result["cpuGovernor"]["value"] == "performance"
    assert result["cpuGovernor"]["ok"] is True


def test_apply_unknown_governor_dry_run(applicator):
    manifest = _manifest_with_performance({"cpuGovernor": "turbo-max"})
    result = applicator.apply(manifest)
    assert result["cpuGovernor"]["ok"] is False


# ── GPU mode tests ─────────────────────────────────────────────────────────────

def test_apply_gpu_mode_dry_run(applicator):
    manifest = _manifest_with_performance({"gpuMode": "performance"})
    result = applicator.apply(manifest)
    assert "gpuMode" in result
    assert result["gpuMode"]["ok"] is True


def test_apply_gpu_mode_nvidia_live():
    """nvidia-smi available → calls nvidia-smi -pm and returns True."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value="/usr/bin/nvidia-smi"), \
         patch("gateos_manager.profile.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = app._apply_gpu_mode("performance", None)
    assert result is True
    # First call should be nvidia-smi -pm
    first_call_args = mock_run.call_args_list[0][0][0]
    assert "nvidia-smi" in first_call_args
    assert "-pm" in first_call_args


def test_apply_gpu_mode_no_gpu_returns_false():
    """No nvidia-smi and no AMD sysfs → returns False."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value=None):
        result = app._apply_gpu_mode("performance", None)
    assert result is False


def test_apply_gpu_mode_nvidia_subprocess_error_returns_false():
    """nvidia-smi raises CalledProcessError → warns and returns False (no AMD path)."""
    import subprocess
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value="/usr/bin/nvidia-smi"), \
         patch("gateos_manager.profile.subprocess.run",
               side_effect=subprocess.CalledProcessError(1, "nvidia-smi")):
        result = app._apply_gpu_mode("performance", None)
    # No AMD card paths exist in test env → applied=False overall
    assert result is False


# ── NIC priority tests ─────────────────────────────────────────────────────────

def test_apply_nic_priority_dry_run(applicator):
    manifest = _manifest_with_performance({"nicPriority": "eth0:100mbit"})
    result = applicator.apply(manifest)
    assert "nicPriority" in result
    assert result["nicPriority"]["ok"] is True


def test_apply_nic_priority_tc_missing():
    """tc not found → returns False."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value=None):
        result = app._apply_nic_priority("eth0:100mbit", None)
    assert result is False


def test_apply_nic_priority_tc_success():
    """tc available → runs qdisc del + add, returns True."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value="/usr/sbin/tc"), \
         patch("gateos_manager.profile.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = app._apply_nic_priority("eth0:100mbit", None)
    assert result is True
    calls = [c[0][0] for c in mock_run.call_args_list]
    assert any("tbf" in args for args in calls)


def test_apply_nic_priority_no_colon_uses_default_rate():
    """Priority without colon uses interface only with default 1gbit rate."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value="/usr/sbin/tc"), \
         patch("gateos_manager.profile.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        app._apply_nic_priority("eth0", None)
    add_call_args = mock_run.call_args_list[-1][0][0]
    assert "1gbit" in add_call_args


def test_apply_nic_priority_tc_error_returns_false():
    """tc add fails → returns False."""
    import subprocess
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value="/usr/sbin/tc"), \
         patch("gateos_manager.profile.subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(returncode=0),  # del succeeds
            subprocess.CalledProcessError(2, "tc", stderr=b"RTNETLINK error"),  # add fails
        ]
        result = app._apply_nic_priority("eth0:100mbit", None)
    assert result is False


# ── Power profile tests ────────────────────────────────────────────────────────

def test_apply_power_profile_dry_run(applicator):
    manifest = _manifest_with_performance({"powerProfile": "performance"})
    result = applicator.apply(manifest)
    assert "powerProfile" in result
    assert result["powerProfile"]["ok"] is True


def test_apply_power_profile_unknown_dry_run(applicator):
    manifest = _manifest_with_performance({"powerProfile": "ultra-boost"})
    result = applicator.apply(manifest)
    assert result["powerProfile"]["ok"] is False


def test_apply_power_profile_tool_missing():
    """powerprofilesctl not installed → returns False."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value=None):
        result = app._apply_power_profile("performance", None)
    assert result is False


def test_apply_power_profile_success():
    """powerprofilesctl available → runs set, returns True."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.shutil.which", return_value="/usr/bin/powerprofilesctl"), \
         patch("gateos_manager.profile.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = app._apply_power_profile("balanced", None)
    assert result is True
    call_args = mock_run.call_args[0][0]
    assert "powerprofilesctl" in call_args
    assert "balanced" in call_args


# ── CPU governor cpufreq unavailable ──────────────────────────────────────────

def test_cpu_governor_no_cpufreq_paths():
    """No cpufreq sysfs → warns and returns False."""
    app = ProfileApplicator(dry_run=False)
    with patch("gateos_manager.profile.Path.exists", return_value=False):
        result = app._apply_cpu_governor("performance", None)
    assert result is False


# ── misc ───────────────────────────────────────────────────────────────────────

def test_apply_empty_performance(applicator):
    manifest = _manifest_with_performance({})
    result = applicator.apply(manifest)
    assert result == {}


def test_apply_no_performance_key(applicator):
    manifest = {"spec": {"profile": {"category": "dev"}, "containers": []}}
    result = applicator.apply(manifest)
    assert result == {}


def test_restore_defaults_dry_run(applicator):
    """restore_defaults should not raise."""
    applicator.restore_defaults()
