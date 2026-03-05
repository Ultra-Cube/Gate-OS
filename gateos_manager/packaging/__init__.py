"""Gate-OS packaging utilities.

Helpers for building distribution packages:
  - .deb package creation via `dpkg-deb`
  - preseed/postinstall script generation for Ubuntu ISO embedding
  - systemd service installation helpers

These are used by ``scripts/build-iso.sh`` and the GitHub Actions ISO workflow.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import Any


GATEOS_USER = "gateos"
GATEOS_GROUP = "gateos"
INSTALL_PREFIX = Path("/usr/local")
SYSTEMD_DIR = Path("/etc/systemd/system")
DATA_DIR = Path("/var/lib/gateos")
RUNTIME_DIR = Path("/run/gateos")


class PackagingError(Exception):
    """Raised when a packaging step fails."""


# ── .deb builder ─────────────────────────────────────────────────────────────

def build_deb(
    src_dir: Path,
    version: str,
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> Path:
    """Build a .deb package for gateos-manager.

    Args:
        src_dir:    Path to the Gate-OS repository root.
        version:    Version string (e.g. "0.2.0").
        output_dir: Where to write the .deb file.
        dry_run:    If True, print commands without executing.

    Returns:
        Path to the generated .deb file.
    """
    pkg_name = f"gateos-manager_{version}_amd64"
    deb_root = output_dir / pkg_name

    # ── DEBIAN control directory ──────────────────────────────────────────────
    debian_dir = deb_root / "DEBIAN"
    _mkdir(debian_dir, dry_run=dry_run)

    control = textwrap.dedent(f"""\
        Package: gateos-manager
        Version: {version}
        Section: utils
        Priority: optional
        Architecture: amd64
        Maintainer: Ultra Cube Tech <support@ucubetech.com>
        Depends: python3 (>= 3.10), python3-yaml, python3-jsonschema, podman | docker.io, systemd
        Recommends: python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1
        Homepage: https://github.com/Ultra-Cube/Gate-OS
        Description: Gate-OS environment manager
         Declarative multi-environment Linux system: switch between gaming, dev,
         design, media, and security environments with sub-3-second latency.
         Includes GTK4/Adwaita UI shell and RESTful Control API.
    """)
    _write_file(debian_dir / "control", control, dry_run=dry_run)

    # postinst: create user, enable service
    postinst = textwrap.dedent(f"""\
        #!/bin/sh
        set -e
        # Create system user if absent
        if ! id -u {GATEOS_USER} >/dev/null 2>&1; then
            useradd --system --no-create-home --group --shell /usr/sbin/nologin {GATEOS_USER}
        fi
        # Ensure state directory
        mkdir -p {DATA_DIR}
        chown {GATEOS_USER}:{GATEOS_GROUP} {DATA_DIR}
        chmod 0750 {DATA_DIR}
        # Enable + start service
        systemctl daemon-reload >/dev/null 2>&1 || true
        systemctl enable gateos-api.service >/dev/null 2>&1 || true
        systemctl start  gateos-api.service >/dev/null 2>&1 || true
    """)
    postinst_path = debian_dir / "postinst"
    _write_file(postinst_path, postinst, dry_run=dry_run)
    _chmod_exec(postinst_path, dry_run=dry_run)

    # prerm: stop service before uninstall
    prerm = textwrap.dedent("""\
        #!/bin/sh
        set -e
        systemctl stop    gateos-api.service >/dev/null 2>&1 || true
        systemctl disable gateos-api.service >/dev/null 2>&1 || true
    """)
    prerm_path = debian_dir / "prerm"
    _write_file(prerm_path, prerm, dry_run=dry_run)
    _chmod_exec(prerm_path, dry_run=dry_run)

    # ── Install tree ──────────────────────────────────────────────────────────
    lib_dir = deb_root / "usr/lib/python3/dist-packages"
    _mkdir(lib_dir, dry_run=dry_run)

    systemd_dest = deb_root / SYSTEMD_DIR.relative_to("/")
    _mkdir(systemd_dest, dry_run=dry_run)

    app_dest = deb_root / "usr/share/applications"
    _mkdir(app_dest, dry_run=dry_run)

    if not dry_run:
        shutil.copytree(
            src_dir / "gateos_manager",
            lib_dir / "gateos_manager",
            dirs_exist_ok=True,
        )
        shutil.copy2(
            src_dir / "data" / "systemd" / "gateos-api.service",
            systemd_dest / "gateos-api.service",
        )
        shutil.copy2(
            src_dir / "data" / "gate-os-manager.desktop",
            app_dest / "gate-os-manager.desktop",
        )
    else:
        print(f"[DRY-RUN] copy gateos_manager → {lib_dir}/gateos_manager")
        print(f"[DRY-RUN] copy gateos-api.service → {systemd_dest}")
        print(f"[DRY-RUN] copy gate-os-manager.desktop → {app_dest}")

    # ── Build the .deb ────────────────────────────────────────────────────────
    deb_path = output_dir / f"{pkg_name}.deb"
    _run(["dpkg-deb", "--build", str(deb_root), str(deb_path)], dry_run=dry_run)
    return deb_path


# ── Preseed / post-install helpers ────────────────────────────────────────────

def generate_preseed(output_path: Path, *, dry_run: bool = False) -> None:
    """Write an Ubuntu auto-install preseed/cloud-init config stub."""
    content = textwrap.dedent("""\
        # Gate-OS Ubuntu 24.04 preseed configuration
        # Used by the ISO builder to auto-configure the installed system.

        # Locale / keyboard
        d-i debian-installer/locale string en_US.UTF-8
        d-i keyboard-configuration/xkb-keymap select us

        # Network
        d-i netcfg/choose_interface select auto
        d-i netcfg/get_hostname string gate-os

        # Time zone
        d-i time/zone string UTC

        # Partitioning (entire disk, ext4)
        d-i partman-auto/method string regular
        d-i partman-auto/choose_recipe select atomic
        d-i partman/confirm_write_new_label boolean true
        d-i partman/confirm boolean true
        d-i partman-md/confirm boolean true
        d-i partman-partitioning/confirm_write_new_label boolean true

        # Default user
        d-i passwd/user-fullname string Gate-OS User
        d-i passwd/username string gateos-user
        d-i passwd/user-password password changeme
        d-i passwd/user-password-again password changeme

        # Package selection
        tasksel tasksel/first multiselect ubuntu-desktop-minimal

        # Post-install: start Gate-OS API
        d-i preseed/late_command string \\
            in-target systemctl enable gateos-api.service; \\
            in-target systemctl enable lightdm.service
    """)
    _write_file(output_path, content, dry_run=dry_run)


def generate_postinstall_script(output_path: Path, *, dry_run: bool = False) -> None:
    """Generate a standalone post-install shell script for overlay installs."""
    content = textwrap.dedent("""\
        #!/usr/bin/env bash
        # Gate-OS post-install overlay script
        # Run after a standard Ubuntu 24.04 install to add Gate-OS on top.
        set -euo pipefail

        echo "[Gate-OS] Installing Gate-OS manager overlay..."

        # Install Python deps
        apt-get update -q
        apt-get install -y python3 python3-pip python3-gi \\
            gir1.2-gtk-4.0 gir1.2-adw-1 podman

        # Install gate-os-manager (pip or .deb)
        if command -v dpkg >/dev/null && ls /opt/gateos/*.deb >/dev/null 2>&1; then
            dpkg -i /opt/gateos/*.deb
        else
            pip3 install --break-system-packages gateos-manager
        fi

        # Enable systemd service
        systemctl enable gateos-api.service
        systemctl start  gateos-api.service

        echo "[Gate-OS] Installation complete!"
        echo "[Gate-OS] Run: gateos-ui    (launch desktop panel)"
        echo "[Gate-OS] Run: gateos api   (start Control API manually)"
    """)
    _write_file(output_path, content, dry_run=dry_run)
    _chmod_exec(output_path, dry_run=dry_run)


# ── Internals ─────────────────────────────────────────────────────────────────

def _mkdir(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] mkdir -p {path}")
    else:
        path.mkdir(parents=True, exist_ok=True)


def _write_file(path: Path, content: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] write {path} ({len(content)} bytes)")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def _chmod_exec(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] chmod +x {path}")
    else:
        path.chmod(path.stat().st_mode | 0o111)


def _run(cmd: list[str], *, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] {' '.join(cmd)}")
    else:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            raise PackagingError(
                f"Command failed: {' '.join(cmd)}\n"
                f"stderr: {result.stderr}"
            )
