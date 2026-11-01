"""Security isolation flags and telemetry for container execution.

This module centralizes future hardening. Currently it only emits log/telemetry
when enforcement is requested. Real profiles will be added later.

Environment Variables:
 - GATEOS_SECURITY_ENFORCE=1  -> enable isolation action (still stub)
 - GATEOS_SECURITY_PROFILE    -> name of profile (future use)
 - GATEOS_SECURITY_READONLY=1 -> mount container root fs read-only + ephemeral overlay
"""
from __future__ import annotations

import os
from typing import Any

from gateos_manager.logging.structured import info, warn
from gateos_manager.telemetry.emitter import emit


def isolation_args(spec: dict[str, Any]) -> list[str]:
    """Return runtime flags for the explicitly requested isolation policy."""
    if os.getenv('GATEOS_SECURITY_ENFORCE') != '1':
        return []
    security = spec.get('security') or {}
    args: list[str] = ['--security-opt', 'no-new-privileges:true']
    apparmor = security.get('appArmorProfile') or os.getenv('GATEOS_SECURITY_PROFILE')
    seccomp = security.get('seccompProfile')
    if apparmor:
        args += ['--security-opt', f'apparmor={apparmor}']
    if seccomp:
        args += ['--security-opt', f'seccomp={seccomp}']
    if os.getenv('GATEOS_SECURITY_READONLY') == '1' or spec.get('readOnlyRootfs'):
        args += ['--read-only', '--tmpfs', '/tmp:rw,noexec,nosuid,nodev']
    if security.get('isolationLevel') == 'strict' or security.get('networkNamespace') == 'none':
        args += ['--network', 'none']
    return args


def apply_isolation(container_name: str, spec: dict[str, Any], correlation_id: str | None = None) -> None:  # pragma: no cover - trivial
    if os.getenv('GATEOS_SECURITY_ENFORCE') != '1':
        return
    profile = os.getenv('GATEOS_SECURITY_PROFILE', 'default')
    emit('security.isolation.apply', container=container_name, profile=profile, correlation_id=correlation_id)
    info('security.isolation.apply', container=container_name, profile=profile, correlation_id=correlation_id)
    flags = isolation_args(spec)
    emit('security.isolation.flags', container=container_name, flags=flags, correlation_id=correlation_id)
    if spec.get('privileged'):
        warn('security.isolation.privileged', container=container_name, correlation_id=correlation_id)

    # Phase 13.3 — read-only root + ephemeral overlay for 'security' environments
    if os.getenv('GATEOS_SECURITY_READONLY') == '1' or spec.get('readOnlyRootfs'):
        _apply_readonly_overlay(container_name, correlation_id)


def _apply_readonly_overlay(container_name: str, correlation_id: str | None = None) -> None:  # pragma: no cover - stub
    """Stub: flag container for read-only root + ephemeral tmpfs overlay.

    In a full implementation this writes OCI spec ``root.readonly = true`` and
    adds a ``/tmp`` tmpfs mount so the container can still create ephemeral
    files. Currently emits telemetry and a log entry.
    """
    emit('security.isolation.readonly_overlay', container=container_name,
         correlation_id=correlation_id)
    info('security.isolation.readonly_overlay', container=container_name,
         correlation_id=correlation_id)


def emit_sbom_generated(image: str, sbom_path: str, format: str = "spdx-json", correlation_id: str | None = None) -> None:
    """Emit a ``sbom_generated`` telemetry event after Syft produces an SBOM.

    Call this from the build / packaging pipeline after running Syft or a
    compatible SBOM tool.  The event is recorded in structured logs and
    forwarded to the OTLP endpoint.

    Args:
        image:          Container image reference (e.g. ``ghcr.io/ultra-cube/gate-os:v1.3.0``).
        sbom_path:      Filesystem path to the generated SBOM file.
        format:         SBOM format string (e.g. ``spdx-json``, ``cyclonedx``).
        correlation_id: Optional request correlation ID.
    """
    emit('sbom_generated', image=image, sbom_path=sbom_path, format=format,
         correlation_id=correlation_id)
    info('sbom_generated', image=image, sbom_path=sbom_path, format=format,
         correlation_id=correlation_id)
