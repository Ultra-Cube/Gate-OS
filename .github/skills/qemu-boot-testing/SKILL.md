---
name: qemu-boot-testing
description: "Use when boot-testing Gate-OS ISO artifacts in QEMU/OVMF, capturing serial logs, screenshots, and install evidence."
---

## Procedure
Pin QEMU/OVMF assumptions; boot BIOS and UEFI; capture serial/QMP evidence; test live session, installer, reboot, sidebar, and switch rollback; publish artifact metadata without secrets.

## Verification
CI job is reproducible, timeouts are bounded, failures retain logs/screenshots, and hardware limitations are recorded.
