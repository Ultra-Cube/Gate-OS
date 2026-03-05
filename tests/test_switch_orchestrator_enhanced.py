"""Tests for the enhanced switch orchestrator (SwitchContext, services, profile, rollback)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gateos_manager.switch.orchestrator import SwitchContext, SwitchError, perform_switch


def test_switch_context_defaults():
    ctx = SwitchContext(environment="dev")
    assert ctx.environment == "dev"
    assert ctx.correlation_id is None
    assert ctx.started_containers == []
    assert ctx.started_services == []
    assert ctx.profile_applied == {}


def test_perform_switch_with_services(tmp_path, monkeypatch):
    """perform_switch should succeed and return containers for a manifest with services."""
    monkeypatch.setenv("GATEOS_CONTAINER_DRY_RUN", "1")

    manifest = {
        "environment": {"name": "svc-env"},
        "containers": [
            {"name": "app", "image": "example/app:latest"},
        ],
        "services": [
            {"name": "docker", "required": False},
        ],
    }
    path = tmp_path / "svc-env.json"
    path.write_text(json.dumps(manifest))

    result = perform_switch(str(path))
    assert result["status"] == "ok"
    assert "app" in result["started_containers"]


def test_perform_switch_missing_manifest(tmp_path):
    with pytest.raises(SwitchError, match="Manifest not found"):
        perform_switch(str(tmp_path / "nonexistent.yaml"))


def test_switch_context_correlation_id():
    ctx = SwitchContext(environment="gaming", correlation_id="test-123")
    assert ctx.correlation_id == "test-123"


def test_switch_context_with_data():
    ctx = SwitchContext(
        environment="dev",
        started_containers=["ctr1", "ctr2"],
        started_services=["docker"],
        profile_applied={"cpuGovernor": {"value": "performance", "ok": True}},
    )
    assert len(ctx.started_containers) == 2
    assert "docker" in ctx.started_services
    assert ctx.profile_applied["cpuGovernor"]["ok"] is True
