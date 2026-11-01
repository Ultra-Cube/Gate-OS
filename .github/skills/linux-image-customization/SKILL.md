---
name: linux-image-customization
description: "Use when unpacking and customizing an Ubuntu/Debian ISO, chroot, initramfs, GRUB, autoinstall, or package layer."
---

## Procedure
Record source ISO checksum and license; unpack; apply pinned package changes in an isolated chroot; add branding and autoinstall configuration; rebuild; generate SBOM and checksums; boot-test.

## Pitfalls
Running host commands in chroot, leaking resolv.conf or credentials, unpinned PPAs, broken initramfs, missing EFI files, and redistributing restricted software.

## Verification
Repeat from a clean input, inspect package provenance, run `systemd-analyze verify` where applicable, boot BIOS/UEFI, and document rollback.
