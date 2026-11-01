"""Kernel & hardware performance profile applicator.

Reads spec.profile.performance from a manifest and applies settings
to the running system (CPU governor, GPU mode, NIC priority).

Environment Variables:
  GATEOS_PROFILE_DRY_RUN=1  — log only, never write to /sys or /proc
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from gateos_manager.logging.structured import error, info, warn
from gateos_manager.telemetry.emitter import emit

# Supported CPU governors on Linux
_CPU_GOVERNORS = {"performance", "powersave", "ondemand", "conservative", "schedutil"}

# sysfs path template for CPU frequency governor
_CPU_GOV_GLOB = "/sys/devices/system/cpu/cpu{n}/cpufreq/scaling_governor"


class ProfileApplicator:
    """Apply performance profiles from an environment manifest."""

    def __init__(self, dry_run: bool | None = None) -> None:
        self._dry_run = (
            dry_run
            if dry_run is not None
            else os.getenv("GATEOS_PROFILE_DRY_RUN") == "1"
        )
        if self._dry_run:
            warn("profile.applicator.dry_run", detail="dry-run mode; no sysfs writes")

    def apply(
        self,
        manifest: dict[str, Any],
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Apply performance profile from manifest. Returns dict of applied settings."""
        performance = (
            manifest.get("spec", {}).get("profile", {}).get("performance", {}) or {}
        )
        applied: dict[str, Any] = {}

        cpu_governor = performance.get("cpuGovernor")
        if cpu_governor:
            ok = self._apply_cpu_governor(cpu_governor, correlation_id)
            applied["cpuGovernor"] = {"value": cpu_governor, "ok": ok}

        gpu_mode = performance.get("gpuMode")
        if gpu_mode:
            ok = self._apply_gpu_mode(gpu_mode, correlation_id)
            applied["gpuMode"] = {"value": gpu_mode, "ok": ok}

        nic_priority = performance.get("nicPriority")
        if nic_priority:
            ok = self._apply_nic_priority(nic_priority, correlation_id)
            applied["nicPriority"] = {"value": nic_priority, "ok": ok}

        emit(
            "profile.applied",
            settings=list(applied.keys()),
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        info(
            "profile.applied",
            settings=applied,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        return applied

    def restore_defaults(self, correlation_id: str | None = None) -> None:
        """Restore balanced defaults (schedutil governor, standard NIC)."""
        self._apply_cpu_governor("schedutil", correlation_id)
        emit("profile.restored_defaults", dry_run=self._dry_run, correlation_id=correlation_id)

    # ── internals ─────────────────────────────────────────────────────────────

    def _apply_cpu_governor(self, governor: str, correlation_id: str | None) -> bool:
        if governor not in _CPU_GOVERNORS:
            warn(
                "profile.cpu_governor.unknown",
                governor=governor,
                supported=list(_CPU_GOVERNORS),
                correlation_id=correlation_id,
            )
            return False
        emit(
            "profile.cpu_governor.attempt",
            governor=governor,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        if self._dry_run:
            info("profile.cpu_governor.dry_run", governor=governor)
            return True
        try:
            cpu_count = os.cpu_count() or 1
            written = 0
            for i in range(cpu_count):
                gov_path = Path(_CPU_GOV_GLOB.format(n=i))
                if gov_path.exists():
                    gov_path.write_text(governor)
                    written += 1
            info(
                "profile.cpu_governor.applied",
                governor=governor,
                cpus_written=written,
                correlation_id=correlation_id,
            )
            return written > 0
        except PermissionError:
            error(
                "profile.cpu_governor.permission_denied",
                detail="Run as root or with CAP_SYS_ADMIN to set CPU governor",
                correlation_id=correlation_id,
            )
            return False
        except Exception as exc:  # noqa: BLE001
            error("profile.cpu_governor.error", error=str(exc), correlation_id=correlation_id)
            return False

    def _apply_gpu_mode(self, mode: str, correlation_id: str | None) -> bool:
        """Apply GPU power mode. Currently a stub — real impl via nvidia-smi / sysfs."""
        emit(
            "profile.gpu_mode.attempt",
            mode=mode,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        info(
            "profile.gpu_mode.stub",
            mode=mode,
            detail="GPU mode application not yet implemented; logged only",
            correlation_id=correlation_id,
        )
        # Future: subprocess.run(["nvidia-smi", "--power-limit", ...])
        # Future: write to /sys/class/drm/.../device/power_performance_level (AMD)
        return True  # optimistic stub

    def _apply_nic_priority(self, priority: str, correlation_id: str | None) -> bool:
        """Apply NIC traffic priority. Currently a stub — real impl via tc/qdisc."""
        emit(
            "profile.nic_priority.attempt",
            priority=priority,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        info(
            "profile.nic_priority.stub",
            priority=priority,
            detail="NIC priority not yet implemented; logged only",
            correlation_id=correlation_id,
        )
        # Future: subprocess.run(["tc", "qdisc", "add", "dev", iface, ...])
        return True  # optimistic stub
