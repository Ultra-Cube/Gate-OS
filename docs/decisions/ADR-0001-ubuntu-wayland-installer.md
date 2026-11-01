# ADR-0001: Ubuntu LTS, Wayland Session, and Installer Boundary

- **Status:** Accepted for Phase 1 alpha
- **Date:** 2026-11-01
- **Owners:** Orchestrator, distro-release-engineer, linux-systems-engineer

## Context

Gate-OS needs a stable installable base for physical hardware and VMs, with a desktop session that can support modern shell work and optional Waydroid. WSL cannot reliably provide loop devices, chroots, firmware boot, or physical installation evidence.

## Decision

1. Keep Ubuntu 24.04 LTS Noble as the Phase 1 base and verify the downloaded upstream ISO against Ubuntu's published SHA-256 manifest before extraction.
2. Target amd64 first; do not imply ARM or broad hardware support until tested.
3. Prefer a Wayland-capable desktop session. The exact shell technology remains a separate ADR after two proof-of-concepts; no claim is made that the current GTK UI is an installed shell.
4. Use an installer boundary that is testable in QEMU. Calamares remains the candidate, but it is not claimed as present until packaged and boot-tested.
5. Keep heavy/proprietary environment components out of the base ISO. Everyday and the environment registry are the first alpha scope; other environments are signed, digest-pinned, opt-in downloads.
6. Run privileged image and boot work in GitHub Actions, a Linux VM, or a documented privileged container, never as an assumption about WSL.

## Options considered

- **Move to a newer non-LTS release:** rejected for Phase 1 stability and support horizon.
- **Build a distro from scratch:** rejected; it expands kernel, installer, hardware, and security ownership before the manager is proven.
- **Default X11 session:** rejected for the Waydroid/modern Wayland target, though fallback support remains a hardware question.
- **Bake all seven environments into the ISO:** rejected for image size, update risk, and license boundaries.

## Consequences

The Phase 1 artifact is amd64-only until evidence expands. Ubuntu package and upstream license obligations remain part of every image build. A Wayland-ready base does not prove every GPU or shell works. Installation, first boot, sidebar, and switch rollback must be demonstrated in QEMU before a release candidate label.

## Evidence required before Checkpoint 1

- Clean CI/VM build from pinned inputs.
- Ubuntu checksum verification and generated SBOM.
- BIOS and UEFI QEMU boot logs/screenshots.
- Fresh VM installation and reboot evidence.
- Everyday environment and one minimal second environment switch with forced rollback test.
- License/security approvals and truthful hardware matrix.
