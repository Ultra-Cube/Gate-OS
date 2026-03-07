"""Kernel & hardware performance profile applicator.

Reads spec.profile.performance from a manifest and applies settings
to the running system (CPU governor, GPU mode, NIC priority, power profile).

Environment Variables:
  GATEOS_PROFILE_DRY_RUN=1  — log only, never write to /sys or /proc
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from gateos_manager.logging.structured import error, info, warn
from gateos_manager.telemetry.emitter import emit

# Supported CPU governors on Linux
_CPU_GOVERNORS = {"performance", "powersave", "ondemand", "conservative", "schedutil"}

# Supported power profiles (powerprofilesctl)
_POWER_PROFILES = {"performance", "balanced", "power-saver"}

# sysfs path template for CPU frequency governor
_CPU_GOV_GLOB = "/sys/devices/system/cpu/cpu{n}/cpufreq/scaling_governor"

# AMD GPU sysfs power level paths (card0 … card3)
_AMD_DPM_GLOB = "/sys/class/drm/card{n}/device/power_dpm_state"
_AMD_PERF_GLOB = "/sys/class/drm/card{n}/device/power_performance_level"

# Map Gate-OS gpuMode values → AMD dpm_state and nvidia-smi profile
_GPU_MODE_AMD: dict[str, str] = {
    "performance": "performance",
    "balanced": "auto",
    "powersave": "battery",
}
_GPU_MODE_NVIDIA_PERSIST: dict[str, str] = {
    "performance": "1",  # persistence mode on
    "balanced": "1",
    "powersave": "0",
}


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

        power_profile = performance.get("powerProfile")
        if power_profile:
            ok = self._apply_power_profile(power_profile, correlation_id)
            applied["powerProfile"] = {"value": power_profile, "ok": ok}

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
            missing = 0
            for i in range(cpu_count):
                gov_path = Path(_CPU_GOV_GLOB.format(n=i))
                if gov_path.exists():
                    gov_path.write_text(governor)
                    written += 1
                else:
                    missing += 1
            if missing > 0 and written == 0:
                warn(
                    "profile.cpu_governor.cpufreq_unavailable",
                    detail="No cpufreq sysfs paths found; acpi-cpufreq or intel_pstate driver may not be loaded",
                    cpus_checked=cpu_count,
                    correlation_id=correlation_id,
                )
                return False
            info(
                "profile.cpu_governor.applied",
                governor=governor,
                cpus_written=written,
                cpus_skipped=missing,
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
        """Apply GPU power mode via nvidia-smi (NVIDIA) or sysfs (AMD)."""
        emit(
            "profile.gpu_mode.attempt",
            mode=mode,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        if self._dry_run:
            info("profile.gpu_mode.dry_run", mode=mode)
            return True

        applied = False

        # ── NVIDIA via nvidia-smi ──────────────────────────────────────────
        if shutil.which("nvidia-smi") is not None:
            try:
                persist = _GPU_MODE_NVIDIA_PERSIST.get(mode, "1")
                subprocess.run(
                    ["nvidia-smi", "-pm", persist],
                    check=True,
                    capture_output=True,
                    timeout=10,
                )
                if mode == "performance":
                    # Maximise clocks for performance profile
                    subprocess.run(
                        ["nvidia-smi", "--auto-boost-default=0"],
                        check=False,
                        capture_output=True,
                        timeout=10,
                    )
                info(
                    "profile.gpu_mode.nvidia_applied",
                    mode=mode,
                    persist=persist,
                    correlation_id=correlation_id,
                )
                applied = True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
                warn(
                    "profile.gpu_mode.nvidia_failed",
                    error=str(exc),
                    correlation_id=correlation_id,
                )

        # ── AMD via sysfs ──────────────────────────────────────────────────
        amd_state = _GPU_MODE_AMD.get(mode)
        if amd_state is not None:
            for card_n in range(4):
                perf_path = Path(_AMD_PERF_GLOB.format(n=card_n))
                dpm_path = Path(_AMD_DPM_GLOB.format(n=card_n))
                if perf_path.exists():
                    try:
                        perf_path.write_text(amd_state)
                        info(
                            "profile.gpu_mode.amd_applied",
                            card=f"card{card_n}",
                            level=amd_state,
                            correlation_id=correlation_id,
                        )
                        applied = True
                    except PermissionError:
                        warn(
                            "profile.gpu_mode.amd_permission_denied",
                            card=f"card{card_n}",
                            correlation_id=correlation_id,
                        )
                elif dpm_path.exists():
                    try:
                        dpm_path.write_text(amd_state)
                        info(
                            "profile.gpu_mode.amd_dpm_applied",
                            card=f"card{card_n}",
                            state=amd_state,
                            correlation_id=correlation_id,
                        )
                        applied = True
                    except PermissionError:
                        warn(
                            "profile.gpu_mode.amd_permission_denied",
                            card=f"card{card_n}",
                            correlation_id=correlation_id,
                        )

        if not applied:
            warn(
                "profile.gpu_mode.no_gpu_found",
                mode=mode,
                detail="Neither nvidia-smi nor AMD sysfs paths found; GPU mode not applied",
                correlation_id=correlation_id,
            )
        return applied

    def _apply_nic_priority(self, priority: str, correlation_id: str | None) -> bool:
        """Apply NIC egress traffic shaping via tc qdisc tbf.

        priority format: "<interface>:<rate>" e.g. "eth0:100mbit"
        If no colon is present the value is treated as interface name only
        and a default rate of 1gbit is used.
        """
        emit(
            "profile.nic_priority.attempt",
            priority=priority,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        if self._dry_run:
            info("profile.nic_priority.dry_run", priority=priority)
            return True

        if shutil.which("tc") is None:
            warn(
                "profile.nic_priority.tc_missing",
                detail="'tc' (iproute2) not found; NIC priority not applied",
                correlation_id=correlation_id,
            )
            return False

        if ":" in priority:
            iface, rate = priority.split(":", 1)
        else:
            iface, rate = priority, "1gbit"

        iface = iface.strip()
        rate = rate.strip()

        try:
            # Delete any existing qdisc on the interface (ignore failure)
            subprocess.run(
                ["tc", "qdisc", "del", "dev", iface, "root"],
                check=False,
                capture_output=True,
                timeout=5,
            )
            # Add tbf qdisc with requested rate
            subprocess.run(
                [
                    "tc", "qdisc", "add", "dev", iface,
                    "root", "tbf",
                    "rate", rate,
                    "burst", "32kbit",
                    "latency", "400ms",
                ],
                check=True,
                capture_output=True,
                timeout=10,
            )
            info(
                "profile.nic_priority.applied",
                iface=iface,
                rate=rate,
                correlation_id=correlation_id,
            )
            return True
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="replace").strip() if exc.stderr else ""
            error(
                "profile.nic_priority.tc_error",
                iface=iface,
                rate=rate,
                stderr=stderr,
                correlation_id=correlation_id,
            )
            return False
        except subprocess.TimeoutExpired:
            error("profile.nic_priority.tc_timeout", iface=iface, correlation_id=correlation_id)
            return False

    def _apply_power_profile(self, profile: str, correlation_id: str | None) -> bool:
        """Apply power profile via powerprofilesctl."""
        emit(
            "profile.power_profile.attempt",
            profile=profile,
            dry_run=self._dry_run,
            correlation_id=correlation_id,
        )
        if profile not in _POWER_PROFILES:
            warn(
                "profile.power_profile.unknown",
                profile=profile,
                supported=list(_POWER_PROFILES),
                correlation_id=correlation_id,
            )
            return False
        if self._dry_run:
            info("profile.power_profile.dry_run", profile=profile)
            return True
        if shutil.which("powerprofilesctl") is None:
            warn(
                "profile.power_profile.tool_missing",
                detail="'powerprofilesctl' not found; install power-profiles-daemon",
                correlation_id=correlation_id,
            )
            return False
        try:
            subprocess.run(
                ["powerprofilesctl", "set", profile],
                check=True,
                capture_output=True,
                timeout=10,
            )
            info(
                "profile.power_profile.applied",
                profile=profile,
                correlation_id=correlation_id,
            )
            return True
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="replace").strip() if exc.stderr else ""
            error(
                "profile.power_profile.error",
                profile=profile,
                stderr=stderr,
                correlation_id=correlation_id,
            )
            return False
        except subprocess.TimeoutExpired:
            error("profile.power_profile.timeout", profile=profile, correlation_id=correlation_id)
            return False
