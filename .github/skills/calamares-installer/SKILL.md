---
name: calamares-installer
description: "Use when configuring or testing the Gate-OS Calamares installer, branding, partitioning, users, bootloader, or post-install hooks."
---

## Procedure
Define supported layouts and data-loss warnings; configure branding and modules; keep post-install actions idempotent and least-privileged; register default environments; test fresh VM installs and failure recovery.

## Pitfalls
Silent destructive partitioning, root-only services without rollback, missing EFI bootloader, locale/RTL regressions, and hooks that assume network access.

## Verification
Install to clean BIOS and UEFI VMs, reboot, verify Gate-OS service/sidebar/environment registry, inspect logs, and test cancel/recovery paths.
