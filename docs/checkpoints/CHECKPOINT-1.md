# Checkpoint 1 — Installable Gate-OS Alpha

**Status:** Pending evidence and maintainer approval  
**Date:** 2026-11-01  
**Branch:** `feat/phase1-installable-iso`

## Completed in this phase slice

- Added [ADR-0001](../decisions/ADR-0001-ubuntu-wayland-installer.md): Ubuntu 24.04 LTS amd64 first, Wayland-capable base, installer boundary, license boundary, and WSL/VM decision.
- Hardened `scripts/build-iso.sh` to verify the exact Ubuntu ISO against the official `SHA256SUMS` manifest before extraction.
- Made `--dry-run` explicitly side-effect-free.
- Added `scripts/qemu-boot-test.sh` with bounded BIOS and UEFI modes and serial-log capture.
- Updated `.github/workflows/build-iso.yml` to install QEMU/OVMF, run checksum verification, execute BIOS/UEFI smoke tests, and upload logs.
- Added `docs/BUILDING.md` and `docs/INSTALL.md` with honest WSL, VM, checksum, Secure Boot, and hardware limitations.
- Updated the reusable ISO skill with checksum and dry-run safety lessons.

## Evidence

- `bash -n scripts/build-iso.sh scripts/qemu-boot-test.sh`: passed.
- Workflow YAML parse: passed.
- `bash scripts/build-iso.sh --dry-run --skip-download`: passed without downloads, mounts, chroot, or writes.
- `make test`: **394 passed**.

## Remaining acceptance blockers

- Real Ubuntu ISO build has not run in this WSL environment; required `xorriso`, `grub-mkrescue`, and `debootstrap` are unavailable.
- No generated ISO, SBOM, detached signature, QEMU BIOS/UEFI logs, or fresh VM installation evidence exists yet.
- Gate-OS service, environment registry, Everyday environment, sidebar, installer, and second-environment rollback still need integration into the image and boot-tested evidence.
- Package inputs and CI actions need immutable pinning and license/security approval before release.

## Decision needed

Approve moving the branch to a Linux VM or GitHub Actions runner for the real build/QEMU loop, or provide a privileged build environment. Do not label `v2.0.0-alpha.1` until the remaining evidence exists.
