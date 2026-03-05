"""Switch orchestrator.

Coordinates the activation of an environment:
 1. Validate manifest (defensive re-validation)
 2. Run pre_switch plugin hooks
 3. Stop conflicting systemd services (ServiceManager)
 4. Apply kernel/hardware performance profile (ProfileApplicator)
 5. Start environment containers (ContainerManager)
 6. Run post_switch plugin hooks
 7. Emit telemetry events

On any failure: rollback (stop started containers, restore services, restore profile).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gateos_manager.containers.manager import ContainerManager
from gateos_manager.logging.structured import error, info, warn
from gateos_manager.manifest.loader import ManifestValidationError, load_manifest
from gateos_manager.plugins.registry import discover_entrypoint_plugins, invoke
from gateos_manager.profile import ProfileApplicator
from gateos_manager.services import ServiceManager
from gateos_manager.telemetry.emitter import emit


class SwitchError(Exception):
    """Raised when a switch operation fails."""


@dataclass
class SwitchContext:
    """Captures pre-switch state for rollback."""

    environment: str
    correlation_id: str | None = None
    started_containers: list[str] = field(default_factory=list)
    started_services: list[str] = field(default_factory=list)
    profile_applied: dict[str, Any] = field(default_factory=dict)


def switch_environment(
    name: str,
    schema_path: Path,
    manifests_dir: Path = Path("examples/environments"),
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Full environment switch with services, profile, containers, hooks, and rollback."""
    discover_entrypoint_plugins()

    ctx = SwitchContext(environment=name, correlation_id=correlation_id)
    container_mgr = ContainerManager()
    service_mgr = ServiceManager()
    profile_app = ProfileApplicator()

    emit("switch.start", environment=name, correlation_id=correlation_id)
    info("switch.start", environment=name, correlation_id=correlation_id)

    manifest: dict[str, Any] | None = None

    try:
        # ── Step 1: Load & validate manifest ─────────────────────────────────
        manifest_path = manifests_dir / f"{name}.yaml"
        manifest = load_manifest(manifest_path, schema_path)

        # ── Step 2: pre_switch hooks ──────────────────────────────────────────
        invoke("pre_switch", environment=name, manifest=manifest)

        # ── Step 3: Start environment services ───────────────────────────────
        ctx.started_services = service_mgr.start_services(manifest, correlation_id=correlation_id)

        # ── Step 4: Apply performance profile ────────────────────────────────
        ctx.profile_applied = profile_app.apply(manifest, correlation_id=correlation_id)

        # ── Step 5: Start containers ──────────────────────────────────────────
        ctx.started_containers = container_mgr.start(manifest, correlation_id=correlation_id)

        # ── Step 6: post_switch hooks ─────────────────────────────────────────
        invoke("post_switch", environment=name, manifest=manifest)

        emit(
            "switch.end",
            environment=name,
            status="success",
            containers=ctx.started_containers,
            services=ctx.started_services,
            correlation_id=correlation_id,
        )
        info(
            "switch.end",
            environment=name,
            status="success",
            containers=ctx.started_containers,
            correlation_id=correlation_id,
        )
        return {
            "status": "success",
            "environment": name,
            "containers": ctx.started_containers,
            "services": ctx.started_services,
            "profile": ctx.profile_applied,
        }

    except Exception as exc:
        _rollback(ctx, manifest, container_mgr, service_mgr, profile_app)
        error("switch.error", environment=name, error=str(exc), correlation_id=correlation_id)
        emit(
            "switch.end",
            environment=name,
            status="error",
            error=str(exc),
            correlation_id=correlation_id,
        )
        invoke("shutdown", environment=name, reason="switch_error")
        raise SwitchError(str(exc)) from exc


def _rollback(
    ctx: SwitchContext,
    manifest: dict[str, Any] | None,
    container_mgr: ContainerManager,
    service_mgr: ServiceManager,
    profile_app: ProfileApplicator,
) -> None:
    """Best-effort rollback on switch failure."""
    warn("switch.rollback.start", environment=ctx.environment, correlation_id=ctx.correlation_id)
    if ctx.started_containers and manifest is not None:
        try:
            container_mgr.stop(manifest, correlation_id=ctx.correlation_id)
        except Exception as exc:  # noqa: BLE001
            error("switch.rollback.containers.error", error=str(exc))
    if ctx.profile_applied:
        try:
            profile_app.restore_defaults(correlation_id=ctx.correlation_id)
        except Exception as exc:  # noqa: BLE001
            error("switch.rollback.profile.error", error=str(exc))
    if ctx.started_services and manifest is not None:
        try:
            service_mgr.stop_services(manifest, correlation_id=ctx.correlation_id)
        except Exception as exc:  # noqa: BLE001
            error("switch.rollback.services.error", error=str(exc))
    emit("switch.rollback.end", environment=ctx.environment, correlation_id=ctx.correlation_id)
    warn("switch.rollback.end", environment=ctx.environment, correlation_id=ctx.correlation_id)


def perform_switch(manifest_path: str | Path, schema_path: Path | None = None) -> dict[str, Any]:
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
    # Name currently unused in dry-run path; may be used later for logging
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
