"""Tests for ProfileApplicator (CPU governor, GPU mode, NIC priority)."""
from __future__ import annotations

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


def test_apply_gpu_mode_stub(applicator):
    manifest = _manifest_with_performance({"gpuMode": "performance"})
    result = applicator.apply(manifest)
    assert "gpuMode" in result
    assert result["gpuMode"]["ok"] is True  # stub always returns True


def test_apply_nic_priority_stub(applicator):
    manifest = _manifest_with_performance({"nicPriority": "high"})
    result = applicator.apply(manifest)
    assert "nicPriority" in result
    assert result["nicPriority"]["ok"] is True  # stub always returns True


def test_apply_empty_performance(applicator):
    manifest = _manifest_with_performance({})
    result = applicator.apply(manifest)
    assert result == {}


def test_apply_no_performance_key(applicator):
    manifest = {"spec": {"profile": {"category": "dev"}, "containers": []}}
    result = applicator.apply(manifest)
    assert result == {}


def test_apply_all_settings(applicator):
    manifest = _manifest_with_performance({
        "cpuGovernor": "performance",
        "gpuMode": "high-performance",
        "nicPriority": "gaming",
    })
    result = applicator.apply(manifest)
    assert len(result) == 3
    assert all(v["ok"] for v in result.values() if v["value"] != "turbo")


def test_restore_defaults_dry_run(applicator):
    """restore_defaults should not raise."""
    applicator.restore_defaults()
