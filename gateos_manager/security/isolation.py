"""Security isolation hooks (seccomp/AppArmor stubs).

This module centralizes future hardening. Currently it only emits log/telemetry
when enforcement is requested. Real profiles will be added later.

Environment Variables:
 - GATEOS_SECURITY_ENFORCE=1  -> enable isolation action (still stub)
 - GATEOS_SECURITY_PROFILE    -> name of profile (future use)
"""
from __future__ import annotations

import os
from typing import Any

from gateos_manager.logging.structured import info, warning
from gateos_manager.telemetry.emitter import emit


def apply_isolation(container_name: str, spec: dict[str, Any], correlation_id: str | None = None) -> None:  # pragma: no cover - trivial
    if os.getenv('GATEOS_SECURITY_ENFORCE') != '1':
        return
    profile = os.getenv('GATEOS_SECURITY_PROFILE', 'default')
    emit('security.isolation.apply', container=container_name, profile=profile, correlation_id=correlation_id)
    info('security.isolation.apply', container=container_name, profile=profile, correlation_id=correlation_id)
    # Future: generate / attach seccomp & AppArmor profiles here.
    if spec.get('privileged'):
        warning('security.isolation.privileged', container=container_name, correlation_id=correlation_id)
