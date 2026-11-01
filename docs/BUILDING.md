# Building Gate-OS

## Current status

The repository contains an Ubuntu 24.04 LTS ISO customization script. It is an engineering build path, not yet a release-proven installable ISO. A real build requires a Linux environment with loop devices, chroot, squashfs, xorriso, GRUB EFI/BIOS tools, and enough disk space.

## WSL limitation

WSL is suitable for editing, tests, dry-runs, and orchestration. Loop mounts, chroot networking, firmware boot, and privileged image operations are not assumed to work in WSL. Run real image builds in GitHub Actions, a privileged Linux dev container explicitly approved for ISO work, or a Linux VM.

## Local checks

```bash
bash -n scripts/build-iso.sh
bash scripts/build-iso.sh --dry-run
make test
```

The dry-run performs no download, mount, chroot, file write, or network operation. It is not evidence that an ISO builds or boots.

## Real build prerequisites

On Ubuntu 24.04, install the reviewed package set:

```bash
sudo apt-get update
sudo apt-get install \
  squashfs-tools xorriso grub-efi-amd64-bin grub-pc-bin \
  mtools debootstrap isolinux syslinux-utils wget qemu-system-x86 ovmf
```

Run from a clean checkout in a disposable build VM:

```bash
sudo -E bash scripts/build-iso.sh --output dist/iso
```

The script downloads the configured Ubuntu base ISO, downloads the official `SHA256SUMS` manifest, verifies the exact ISO filename, customizes the extracted filesystem, repacks it, builds the ISO, and writes a `.sha256` file. Do not use `--skip-download` unless the cached ISO has independently been verified.

## Reproducibility and provenance

Record Ubuntu URL, checksum manifest URL, package snapshot, Gate-OS commit, tool versions, build host, and output checksum. Generate an SBOM before release. Never add proprietary applications or secrets to the image. See [LICENSES-AND-THIRD-PARTY.md](LICENSES-AND-THIRD-PARTY.md).

## Boot smoke test

```bash
bash scripts/qemu-boot-test.sh dist/iso/gate-os-noble-amd64-VERSION.iso
```

The smoke test is bounded and stores serial output. It does not replace a fresh install test or hardware matrix.
