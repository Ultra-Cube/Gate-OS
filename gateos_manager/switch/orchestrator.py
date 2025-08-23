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


class SwitchError(Exception):
    """Raised when a switch operation fails."""


def switch_environment(name: str, schema_path: Path, manifests_dir: Path = Path("examples/environments")) -> Dict[str, Any]:
    emit("switch.start", environment=name)
    try:
        manifest_path = manifests_dir / f"{name}.yaml"
        manifest = load_manifest(manifest_path, schema_path)
        # TODO: container/service orchestration
        emit("switch.end", environment=name, status="success")
        return {"status": "success", "environment": name}
    except ManifestValidationError as e:  # pragma: no cover - simple path
        emit("switch.end", environment=name, status="error", error=str(e))
        raise SwitchError(str(e)) from e
    except Exception as e:  # pragma: no cover - future expansion
        emit("switch.end", environment=name, status="error", error=str(e))
        raise SwitchError(str(e)) from e
