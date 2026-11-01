---
name: linux-iso-build
description: "Use when building or reviewing a bootable Gate-OS hybrid ISO with live-build, debootstrap, or an equivalent reproducible flow."
---

## Procedure
1. Confirm base release, package layers, architecture, size budget, and license matrix.
2. Build in CI, a VM, or a documented privileged container; do not rely on WSL loop devices.
3. Generate live filesystem, installer, BIOS/UEFI boot entries, checksums, SBOM, and detached signature.
4. Boot-test with QEMU/OVMF and capture serial and screenshot evidence.

## Commands
`make iso`, `qemu-system-x86_64 -enable-kvm -bios OVMF_CODE.fd`, `sha256sum`, `syft`, and `gpg --verify` as configured by the repository.

## Pitfalls
Mutable apt repositories, unsigned downloads, proprietary packages, non-reproducible timestamps, testing only one firmware mode, and dry-run code that still performs command substitutions or writes files. Make dry-run an explicit side-effect-free branch; verify the upstream checksum manifest before mounting or extracting any ISO.

## Verification
Build succeeds from a clean runner; checksum/signature verify; BIOS and UEFI boot; live session and installer work; artifacts and limitations are documented.

For WSL, run `bash scripts/build-iso.sh --dry-run` locally and perform real loop-device, chroot, and QEMU work in CI or a privileged Linux VM. A successful dry-run is not ISO evidence.

Authoritative references: Ubuntu live-build/debootstrap docs, Debian live-manual, Calamares docs, QEMU and OVMF docs.
