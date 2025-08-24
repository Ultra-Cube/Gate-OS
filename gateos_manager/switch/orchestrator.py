"""Switch orchestrator stub.

Coordinates the activation of an environment. Real implementation will:
 - Validate manifest again (defensive)
 - Stop conflicting services
 - Start containers / apply profiles
 - Emit telemetry events

Current stub just emits start/end telemetry events and returns success.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from gateos_manager.manifest.loader import load_manifest, ManifestValidationError
from gateos_manager.telemetry.emitter import emit
from gateos_manager.logging.structured import info, error
from gateos_manager.plugins.registry import invoke
from gateos_manager.plugins.registry import invoke, discover_entrypoint_plugins
from gateos_manager.containers.manager import ContainerManager


class SwitchError(Exception):
    """Raised when a switch operation fails."""


def switch_environment(name: str, schema_path: Path, manifests_dir: Path = Path("examples/environments"), correlation_id: str | None = None) -> Dict[str, Any]:
    # Ensure entrypoint plugins loaded (CLI path)
    discover_entrypoint_plugins()
    emit("switch.start", environment=name, correlation_id=correlation_id)
    info("switch.start", environment=name, correlation_id=correlation_id)
    manager = ContainerManager()
    started: list[str] = []
    try:
        manifest_path = manifests_dir / f"{name}.yaml"
        manifest = load_manifest(manifest_path, schema_path)
        invoke("pre_switch", environment=name, manifest=manifest)
        started = manager.start(manifest, correlation_id=correlation_id)
        invoke("post_switch", environment=name, manifest=manifest)
        emit("switch.end", environment=name, status="success", containers=started, correlation_id=correlation_id)
        info("switch.end", environment=name, status="success", containers=started, correlation_id=correlation_id)
        return {"status": "success", "environment": name, "containers": started}
    except ManifestValidationError as e:  # pragma: no cover - simple path
        emit("switch.end", environment=name, status="error", error=str(e), correlation_id=correlation_id)
        error("switch.error", environment=name, error=str(e), correlation_id=correlation_id)
        if started:
            manager.stop(manifest, correlation_id=correlation_id)  # type: ignore
        invoke("shutdown", environment=name, reason="validation_error")
        raise SwitchError(str(e)) from e


def perform_switch(manifest_path: str | Path, schema_path: Path | None = None) -> Dict[str, Any]:
    """Convenience helper used in tests to perform a switch given a direct manifest file.

    Accepts JSON or YAML manifest. Uses ContainerManager in dry-run mode when no runtime.
    Returns a standardized result dict: {status, started_containers}.
    """
    path = Path(manifest_path)
    if not path.exists():  # pragma: no cover - defensive
        raise SwitchError(f"Manifest not found: {path}")
    # Infer schema path if not provided (fallback to docs schema for legacy tests)
    schema_path = schema_path or Path('gateos_manager/manifest/schemas/environment-manifest-v1.0.yaml')
    # Load JSON or YAML
    text = path.read_text()
    if path.suffix == '.json':
        import json
        manifest = json.loads(text)
    else:
        import yaml  # type: ignore
        manifest = next(iter(list(yaml.safe_load_all(text))) or [{}])
    name = manifest.get('name') or manifest.get('environment', {}).get('name') or 'env'
    manager = ContainerManager()
    try:
        started_raw = manager.start(manifest)
        # Map back to spec names if prefixed (gateos_<env>_<name>)
        started = []
        for cname in started_raw:
            if cname.startswith('gateos_'):
                parts = cname.split('_', 2)
                if len(parts) == 3:
                    started.append(parts[2])
                    continue
            started.append(cname)
        return {"status": "ok", "started_containers": started}
    except Exception as e:  # pragma: no cover - simple
        raise SwitchError(str(e)) from e
