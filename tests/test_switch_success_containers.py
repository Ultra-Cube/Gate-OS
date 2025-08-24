import json

from gateos_manager.switch.orchestrator import perform_switch


def test_switch_success_containers(tmp_path, monkeypatch):
    """Integration test: successful switch returns started containers list.

    Uses dry-run container runtime (forced via env) to avoid real engine dependency.
    """
    # Force dry-run runtime detection
    monkeypatch.setenv('GATEOS_DRY_RUN', '1')

    manifest = {
        "environment": {
            "name": "success-env",
            "description": "Test Env"
        },
        "containers": [
            {"name": "alpha", "image": "example/alpha:latest"},
            {"name": "beta", "image": "example/beta:latest"}
        ]
    }
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest))

    result = perform_switch(str(manifest_path))
    assert result["status"] == "ok"
    started = result.get("started_containers") or result.get("containers_started") or []
    # Our orchestrator returns 'started_containers' - keep fallback for forward compat
    assert set(started) == {"alpha", "beta"}
