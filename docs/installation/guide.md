---
title: Gate-OS Installation Guide
project: Gate-OS
owner: Ultra Cube Tech
status: Active
last-updated: 2026-03-05
---

# Gate-OS Installation Guide

> Gate-OS v0.2.0 — Ubuntu 24.04 LTS base

---

## Overview

Gate-OS is distributed as a bootable ISO image built on **Ubuntu 24.04 LTS "Noble Numbat"**.
It can be installed on physical hardware or a virtual machine, or run as a live session.

### Two installation methods

| Method | Best For | Effort |
|--------|----------|--------|
| [ISO Install](#method-1-iso-install) | New machines / dedicated hardware | Low |
| [Overlay Install](#method-2-overlay-on-existing-ubuntu) | Existing Ubuntu 24.04 systems | Very Low |

---

## Prerequisites

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores (x86_64) | 4+ cores |
| RAM | 2 GB | 8 GB |
| Storage | 20 GB | 50 GB SSD |
| GPU | Any | NVIDIA (for gaming profile) |
| Network | — | 1 Gbps (for container pulls) |

---

## Method 1: ISO Install

### Step 1 — Download the ISO

The latest ISO is published on [GitHub Releases](https://github.com/Ultra-Cube/Gate-OS/releases).

```bash
# Download latest ISO
wget https://github.com/Ultra-Cube/Gate-OS/releases/latest/download/gate-os-noble-amd64-0.2.0.iso

# Verify SHA-256 checksum
wget https://github.com/Ultra-Cube/Gate-OS/releases/latest/download/gate-os-noble-amd64-0.2.0.iso.sha256
sha256sum --check gate-os-noble-amd64-0.2.0.iso.sha256
```

### Step 2 — Flash to USB

**Option A: Ventoy (recommended)**

1. Install [Ventoy](https://www.ventoy.net/) on a USB drive (≥ 8 GB).
2. Copy the `.iso` file to the Ventoy USB partition.
3. Boot the USB and select Gate-OS from the Ventoy menu.

**Option B: `dd` (Linux)**

```bash
# Replace /dev/sdX with your USB device
sudo dd if=gate-os-noble-amd64-0.2.0.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

**Option C: Rufus (Windows)**

1. Open [Rufus](https://rufus.ie/).
2. Select the ISO → GPT partition → UEFI (non-CSM).
3. Write.

### Step 3 — Boot and Install

1. Boot from the USB drive.
2. Select **"Install Gate-OS"** from the GRUB menu.
3. Follow the Ubuntu installer wizard.
4. The Gate-OS manager is auto-configured during post-install.

### Step 4 — First Login

After installation:

```bash
# Verify Gate-OS API is running
systemctl status gateos-api.service

# Launch the environment manager UI
gateos-ui

# Or use the CLI
gateos validate examples/environments/*.yaml
gateos switch dev
```

---

## Method 2: Overlay on Existing Ubuntu

If you already have **Ubuntu 24.04 LTS** installed, you can add Gate-OS on top:

```bash
# Clone the repository
git clone https://github.com/Ultra-Cube/Gate-OS.git
cd Gate-OS

# Run the overlay installer (requires sudo for systemd setup)
sudo bash scripts/install-dde.sh   # Optional: Deepin Desktop

# Install Gate-OS manager
pip3 install --break-system-packages -e ".[ui]"

# Install and enable the systemd service
sudo cp data/systemd/gateos-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gateos-api.service

# Verify
gateos --help
gateos-ui
```

---

## Building the ISO Yourself

See [`scripts/build-iso.sh`](../../scripts/build-iso.sh) for the full build script.

```bash
# Prerequisites (Ubuntu 24.04 host)
sudo apt install squashfs-tools xorriso grub-efi-amd64-bin debootstrap

# Build
./scripts/build-iso.sh --version 0.2.0 --output dist/iso

# The ISO will be at:
ls dist/iso/gate-os-noble-amd64-0.2.0.iso
```

The GitHub Actions workflow [`.github/workflows/build-iso.yml`](../../.github/workflows/build-iso.yml)
builds and publishes the ISO automatically on every release tag.

---

## Post-Install Configuration

### Generate an API token

```bash
# Generate a 48-character token
gateos gen-token --length 48 | sudo tee /var/lib/gateos/api.token
sudo chown gateos:gateos /var/lib/gateos/api.token
sudo chmod 0600 /var/lib/gateos/api.token

# Export for CLI use
export GATEOS_API_TOKEN=$(sudo cat /var/lib/gateos/api.token)
```

### Validate your environment manifests

```bash
gateos validate examples/environments/*.yaml
```

### Switch environments

```bash
# Switch to development environment
gateos switch dev

# Switch to gaming environment
gateos switch gaming

# Or use the UI
gateos-ui
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `gateos-api.service` fails to start | Check `journalctl -u gateos-api -n 50` |
| UI won't launch: `GtkNotAvailable` | `sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1` |
| `podman` not found | `sudo apt install podman` |
| API returns 401 Unauthorized | Set `GATEOS_API_TOKEN` or `GATEOS_API_TOKEN_FILE` |
| Switch timeout | Increase `GATEOS_CONTAINER_START_TIMEOUT` (default: 30s) |

---

## Supported Environments

| Environment | Description | Key Tools |
|-------------|-------------|-----------|
| `dev` | Software development | VS Code, Git, Docker, Node.js, Python |
| `gaming` | Gaming + Steam | Steam, Proton, Lutris, MangoHUD |
| `design` | Creative design | GIMP, Inkscape, Blender, Kdenlive |
| `media` | Media & streaming | VLC, OBS Studio, Ardour |
| `security` | Security research | Kali tools (containerized), Wireshark, Burp |

---

*For more information see [docs/README.md](../README.md) or open an issue on GitHub.*

**Last Updated:** March 2026 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
