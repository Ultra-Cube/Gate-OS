from pathlib import Path
import pytest
from gateos_manager.plugins import registry
from gateos_manager.switch.orchestrator import switch_environment, SwitchError


def test_shutdown_hook_called_on_validation_error(tmp_path):
    # register shutdown hook
    calls = []
    def shutdown_hook(environment, reason):  # noqa: D401
        calls.append((environment, reason))
    registry.register('shutdown', shutdown_hook)

    # Provide schema path but missing manifest file will cause validation/load error
    schema_path = Path('docs/architecture/schemas/environment-manifest.schema.yaml')
    with pytest.raises(SwitchError):
        switch_environment('nonexistent_env', schema_path, manifests_dir=tmp_path)
    assert calls and calls[0][0] == 'nonexistent_env'
