"""SystemD service orchestration for Gate-OS environment switching.

Manages stopping conflicting services from the previous environment
and starting services required by the target environment manifest.

Environment Variables:
  GATEOS_SYSTEMD_DRY_RUN=1  — force dry-run (never call systemctl)

Manifest Contract (spec.services):
  services:
    - name: "docker"
      required: true
    - name: "bluetooth"
      required: false
"""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from gateos_manager.logging.structured import error, info, warn
from gateos_manager.telemetry.emitter import emit


class ServiceError(Exception):
    """Raised when a critical service operation fails."""


class ServiceManager:
    """Manage systemd services across environment switches."""

    def __init__(self, dry_run: bool | None = None) -> None:
        self._dry_run = (
            dry_run
            if dry_run is not None
            else (
                os.getenv("GATEOS_SYSTEMD_DRY_RUN") == "1"
                or not shutil.which("systemctl")
            )
        )
        if self._dry_run:
            warn("service.manager.dry_run", detail="systemctl not found or dry-run forced")

    # ── public API ────────────────────────────────────────────────────────────

    def start_services(
        self,
        manifest: dict[str, Any],
        correlation_id: str | None = None,
    ) -> list[str]:
        """Start services declared in manifest spec.services (required=True).

        Returns list of service names successfully started.
        """
        services = self._get_services(manifest)
        started: list[str] = []
        for svc in services:
            name = svc.get("name", "")
            required = svc.get("required", False)
            if not name:
                continue
            ok = self._systemctl("start", name, correlation_id=correlation_id)
            if ok:
                started.append(name)
            elif required:
                raise ServiceError(f"Required service '{name}' failed to start")
        return started

    def stop_services(
        self,
        manifest: dict[str, Any],
        correlation_id: str | None = None,
    ) -> list[str]:
        """Stop services declared in manifest spec.services.

        Returns list of service names successfully stopped.
        """
        services = self._get_services(manifest)
        stopped: list[str] = []
        for svc in services:
            name = svc.get("name", "")
            if not name:
                continue
            ok = self._systemctl("stop", name, correlation_id=correlation_id)
            if ok:
                stopped.append(name)
        return stopped

    def is_active(self, service_name: str) -> bool:
        """Return True if service is currently active (running)."""
        if self._dry_run:
            return False
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "--quiet", service_name],
                check=False,
                capture_output=True,
            )
            return result.returncode == 0
        except Exception:  # noqa: BLE001
            return False

    def status(self, manifest: dict[str, Any]) -> dict[str, str]:
        """Return a dict of {service_name: active|inactive|unknown} for manifest services."""
        services = self._get_services(manifest)
        result: dict[str, str] = {}
        for svc in services:
            name = svc.get("name", "")
            if not name:
                continue
            if self._dry_run:
                result[name] = "unknown (dry-run)"
            elif self.is_active(name):
                result[name] = "active"
            else:
                result[name] = "inactive"
        return result

    # ── internals ─────────────────────────────────────────────────────────────

    @staticmethod
    def _get_services(manifest: dict[str, Any]) -> list[dict[str, Any]]:
        return manifest.get("spec", {}).get("services", []) or []

    def _systemctl(
        self,
        action: str,
        service: str,
        correlation_id: str | None = None,
    ) -> bool:
        """Run systemctl <action> <service>. Returns True on success."""
        emit(
            f"service.{action}.attempt",
            service=service,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        info(
            f"service.{action}.attempt",
            service=service,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        if self._dry_run:
            emit(
                f"service.{action}",
                service=service,
                status="ok",
                dry_run=True,
                correlation_id=correlation_id,
            )
            return True
        try:
            subprocess.run(
                ["systemctl", action, service],
                check=True,
                capture_output=True,
                timeout=30,
            )
            emit(
                f"service.{action}",
                service=service,
                status="ok",
                correlation_id=correlation_id,
            )
            info(
                f"service.{action}.ok",
                service=service,
                correlation_id=correlation_id,
            )
            return True
        except subprocess.CalledProcessError as e:
            error(
                f"service.{action}.error",
                service=service,
                returncode=e.returncode,
                correlation_id=correlation_id,
            )
            emit(
                f"service.{action}",
                service=service,
                status="error",
                returncode=e.returncode,
                correlation_id=correlation_id,
            )
            return False
        except subprocess.TimeoutExpired:
            error(
                f"service.{action}.timeout",
                service=service,
                correlation_id=correlation_id,
            )
            return False
        except Exception as exc:  # noqa: BLE001
            error(
                f"service.{action}.exception",
                service=service,
                error=str(exc),
                correlation_id=correlation_id,
            )
            return False
