# Installing Gate-OS (Phase 1 alpha scope)

## Status

An installable release artifact is not yet published from this branch. This document defines the verification procedure and must be updated with a release URL only after a CI/VM install succeeds.

## Before installation

- Back up personal data.
- Confirm the release architecture and tested hardware matrix.
- Verify `SHA256SUMS` and the detached signature when published.
- Use a spare USB or a VM; installation can erase a selected disk.

## VM verification

Use QEMU/OVMF for BIOS and UEFI tests. Allocate enough memory for the Ubuntu desktop base and capture serial/screenshot artifacts. Test live boot, installer, reboot, Gate-OS service, sidebar, Everyday environment, and rollback from a forced switch failure.

## Physical media

When a verified release exists, write the ISO with Rufus, balenaEtcher, or `dd` only after checksum/signature verification. Select the correct removable device and never assume `/dev/sdX`.

## Secure Boot and drivers

Secure Boot support, NVIDIA proprietary drivers, and other hardware-specific packages are not claimed until tested and documented. Proprietary drivers are user-downloaded under their own licenses and are not redistributed by the ISO.

## Troubleshooting

Collect boot mode, GPU, kernel, installer logs, Gate-OS service status, and exact image checksum. Do not paste tokens or private logs into issues. Unsupported hardware should be recorded in the hardware matrix rather than described as generally compatible.
