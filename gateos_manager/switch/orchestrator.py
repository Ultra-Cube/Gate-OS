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
from gateos_manager.containers.manager import ContainerManager


class SwitchError(Exception):
    """Raised when a switch operation fails."""


def switch_environment(name: str, schema_path: Path, manifests_dir: Path = Path("examples/environments"), correlation_id: str | None = None) -> Dict[str, Any]:
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
    except Exception as e:  # pragma: no cover - future expansion
        emit("switch.end", environment=name, status="error", error=str(e), correlation_id=correlation_id)
        error("switch.error", environment=name, error=str(e), correlation_id=correlation_id)
        if started:
            manager.stop(manifest, correlation_id=correlation_id)  # type: ignore
        invoke("shutdown", environment=name, reason="exception")
        raise SwitchError(str(e)) from e
