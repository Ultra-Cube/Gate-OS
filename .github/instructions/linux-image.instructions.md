---
applyTo: "packaging/**,iso/**,live-build/**,**/chroot/**,**/preseed/**,**/autoinstall/**,**/calamares/**"
description: "Linux image, installer, live-build, and chroot guidance"
---

Keep image builds reproducible and non-interactive. Separate base, desktop, Gate-OS, and environment packages. Never copy proprietary packages into redistributable images without a documented license decision. Verify package signatures, generate checksums and SBOMs, and boot-test BIOS and UEFI images with QEMU/OVMF. Document WSL limitations and privileged build requirements.
