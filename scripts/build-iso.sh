#!/usr/bin/env bash
# =============================================================================
# Gate-OS ISO Builder
# =============================================================================
# Builds a bootable Gate-OS ISO image based on Ubuntu 24.04 LTS "Noble Numbat".
# Embeds the gate-os-manager Python package and auto-configures systemd services.
#
# Prerequisites (install on Ubuntu 24.04):
#   sudo apt install cubic live-build debootstrap squashfs-tools xorriso \
#                    isolinux syslinux-utils grub-efi-amd64-bin mtools
#
# Usage:
#   ./scripts/build-iso.sh [OPTIONS]
#
# Options:
#   --output DIR      Output directory (default: ./dist/iso)
#   --name NAME       ISO filename stem (default: gate-os-noble-amd64)
#   --version VER     Gate-OS version string (default: read from pyproject.toml)
#   --skip-download   Reuse existing Ubuntu base ISO in /tmp/ubuntu-base.iso
#   --dry-run         Print commands without executing them
#
# Environment Variables:
#   UBUNTU_ISO_URL    Override upstream Ubuntu 24.04 LTS ISO download URL
#   GATEOS_VERSION    Gate-OS version string (overrides --version)
#
# =============================================================================
set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/dist/iso"
ISO_STEM="gate-os-noble-amd64"
GATEOS_VERSION="${GATEOS_VERSION:-$(python3 -c "import tomllib; d=tomllib.load(open('${REPO_ROOT}/pyproject.toml','rb')); print(d['project']['version'])" 2>/dev/null || echo "0.2.0")}"
UBUNTU_BASE_ISO="/tmp/ubuntu-base-24.04.iso"
UBUNTU_ISO_URL="${UBUNTU_ISO_URL:-https://releases.ubuntu.com/24.04/ubuntu-24.04.1-desktop-amd64.iso}"
SKIP_DOWNLOAD=false
DRY_RUN=false
BUILD_DIR="/tmp/gateos-iso-build"
CHROOT_DIR="${BUILD_DIR}/chroot"
ISO_ROOT="${BUILD_DIR}/iso-root"

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
die()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
run()   {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $*"
    else
        "$@"
    fi
}

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output)    OUTPUT_DIR="$2"; shift 2 ;;
        --name)      ISO_STEM="$2"; shift 2 ;;
        --version)   GATEOS_VERSION="$2"; shift 2 ;;
        --skip-download) SKIP_DOWNLOAD=true; shift ;;
        --dry-run)   DRY_RUN=true; shift ;;
        *) die "Unknown option: $1" ;;
    esac
done

ISO_OUTPUT="${OUTPUT_DIR}/${ISO_STEM}-${GATEOS_VERSION}.iso"

# ── Preflight checks ──────────────────────────────────────────────────────────
preflight() {
    info "Checking build prerequisites..."
    local missing=()
    for cmd in unsquashfs mksquashfs xorriso grub-mkrescue debootstrap; do
        command -v "$cmd" &>/dev/null || missing+=("$cmd")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        warn "Missing tools: ${missing[*]}"
        warn "Install with:"
        warn "  sudo apt install squashfs-tools xorriso grub-efi-amd64-bin debootstrap"
        [[ "$DRY_RUN" == "false" ]] && die "Cannot build ISO without required tools."
    fi
    ok "Prerequisites satisfied (or dry-run mode)"
}

# ── Step 1: Download Ubuntu base ISO ─────────────────────────────────────────
download_base_iso() {
    if [[ -f "$UBUNTU_BASE_ISO" && "$SKIP_DOWNLOAD" == "true" ]]; then
        ok "Reusing existing Ubuntu base ISO: $UBUNTU_BASE_ISO"
        return
    fi
    info "Downloading Ubuntu 24.04 LTS base ISO..."
    info "URL: ${UBUNTU_ISO_URL}"
    run wget -q --show-progress -O "$UBUNTU_BASE_ISO" "$UBUNTU_ISO_URL"
    ok "Ubuntu base ISO saved to $UBUNTU_BASE_ISO"
}

# ── Step 2: Extract ISO filesystem ──────────────────────────────────────────
extract_iso() {
    info "Extracting Ubuntu base ISO filesystem..."
    run rm -rf "$BUILD_DIR" && run mkdir -p "$ISO_ROOT" "$CHROOT_DIR"

    # Mount ISO (requires loop device)
    local MOUNT_DIR="${BUILD_DIR}/mnt"
    run mkdir -p "$MOUNT_DIR"
    run mount -o loop,ro "$UBUNTU_BASE_ISO" "$MOUNT_DIR"
    run cp -a "${MOUNT_DIR}/." "${ISO_ROOT}/"
    run umount "$MOUNT_DIR"

    # Extract squashfs to chroot
    local SQUASHFS
    SQUASHFS=$(find "${ISO_ROOT}" -name "*.squashfs" | head -1)
    [[ -z "$SQUASHFS" ]] && die "No squashfs found in ISO."
    info "Extracting squashfs: $SQUASHFS"
    run unsquashfs -f -d "$CHROOT_DIR" "$SQUASHFS"
    ok "Filesystem extracted to $CHROOT_DIR"
}

# ── Step 3: Chroot customization ─────────────────────────────────────────────
customize_chroot() {
    info "Customizing chroot: installing Gate-OS manager..."

    # Copy repo into chroot for installation
    run mkdir -p "${CHROOT_DIR}/opt/gateos-src"
    run cp -r "${REPO_ROOT}/gateos_manager" "${CHROOT_DIR}/opt/gateos-src/"
    run cp "${REPO_ROOT}/pyproject.toml" "${CHROOT_DIR}/opt/gateos-src/"
    run cp "${REPO_ROOT}/README.md" "${CHROOT_DIR}/opt/gateos-src/"

    # Copy systemd service files
    run mkdir -p "${CHROOT_DIR}/etc/systemd/system"
    run cp "${REPO_ROOT}/data/systemd/gateos-api.service" \
           "${CHROOT_DIR}/etc/systemd/system/" 2>/dev/null || \
        warn "gateos-api.service not found (will be created in Phase 4)"

    # Copy desktop file
    run mkdir -p "${CHROOT_DIR}/usr/share/applications"
    run cp "${REPO_ROOT}/data/gate-os-manager.desktop" \
           "${CHROOT_DIR}/usr/share/applications/"

    # Write chroot install script
    cat > "${BUILD_DIR}/chroot-install.sh" << 'CHROOT_SCRIPT'
#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# Install Python + PyGObject + system deps
apt-get update -q
apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-gi \
    gir1.2-gtk-4.0 gir1.2-adw-1 \
    gir1.2-ayatanaappindicator3-0.1 \
    python3-yaml python3-jsonschema \
    podman systemd

# Install gateos-manager
pip3 install --break-system-packages /opt/gateos-src/

# Enable Gate-OS API service on boot
systemctl enable gateos-api.service 2>/dev/null || true

# Set hostname
echo "gate-os" > /etc/hostname

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/*
CHROOT_SCRIPT

    run chmod +x "${BUILD_DIR}/chroot-install.sh"
    run cp "${BUILD_DIR}/chroot-install.sh" "${CHROOT_DIR}/chroot-install.sh"

    if [[ "$DRY_RUN" == "false" ]]; then
        # Bind mounts for chroot
        mount --bind /dev  "${CHROOT_DIR}/dev"
        mount --bind /proc "${CHROOT_DIR}/proc"
        mount --bind /sys  "${CHROOT_DIR}/sys"

        chroot "${CHROOT_DIR}" /bin/bash /chroot-install.sh

        # Cleanup bind mounts
        umount "${CHROOT_DIR}/dev"  || true
        umount "${CHROOT_DIR}/proc" || true
        umount "${CHROOT_DIR}/sys"  || true
    fi
    ok "Chroot customization complete"
}

# ── Step 4: Re-pack squashfs ─────────────────────────────────────────────────
repack_squashfs() {
    info "Repacking squashfs filesystem..."
    local SQUASHFS_OUT="${ISO_ROOT}/casper/filesystem.squashfs"
    run rm -f "$SQUASHFS_OUT"
    run mksquashfs "$CHROOT_DIR" "$SQUASHFS_OUT" \
        -comp xz -Xbcj x86 -b 1M -no-progress
    # Update filesystem size
    run bash -c "printf $(du -sx --block-size=1 "${CHROOT_DIR}" | cut -f1) > '${ISO_ROOT}/casper/filesystem.size'"
    ok "Squashfs repacked: $SQUASHFS_OUT"
}

# ── Step 5: Set Gate-OS branding ─────────────────────────────────────────────
apply_branding() {
    info "Applying Gate-OS branding to ISO..."

    # Update GRUB menu title
    local GRUB_CFG="${ISO_ROOT}/boot/grub/grub.cfg"
    if [[ -f "$GRUB_CFG" ]]; then
        run sed -i \
            "s/Ubuntu/Gate-OS ${GATEOS_VERSION}/g; \
             s/ubuntu/gate-os/g" \
            "$GRUB_CFG"
    fi

    # Write .disk/info
    run mkdir -p "${ISO_ROOT}/.disk"
    echo "Gate-OS ${GATEOS_VERSION} \"Noble\" - Release amd64 ($(date +%Y%m%d))" \
        > "${ISO_ROOT}/.disk/info"

    ok "Branding applied"
}

# ── Step 6: Build final ISO ──────────────────────────────────────────────────
build_iso() {
    info "Building final ISO: $ISO_OUTPUT"
    run mkdir -p "$OUTPUT_DIR"
    run xorriso \
        -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "GATE_OS_$(echo "$GATEOS_VERSION" | tr '.' '_')" \
        -output "$ISO_OUTPUT" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        --eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-gpt-basdat \
        "$ISO_ROOT"
    ok "ISO built: $ISO_OUTPUT"
}

# ── Step 7: Checksum ─────────────────────────────────────────────────────────
generate_checksum() {
    info "Generating SHA-256 checksum..."
    run bash -c "sha256sum '${ISO_OUTPUT}' > '${ISO_OUTPUT}.sha256'"
    ok "Checksum: ${ISO_OUTPUT}.sha256"
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     Gate-OS ISO Builder v${GATEOS_VERSION}        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "  Base OS  : Ubuntu 24.04 LTS Noble Numbat"
    echo "  Output   : $ISO_OUTPUT"
    echo "  Dry-run  : $DRY_RUN"
    echo ""

    preflight
    download_base_iso
    extract_iso
    customize_chroot
    repack_squashfs
    apply_branding
    build_iso
    generate_checksum

    echo ""
    ok "════════════════════════════════════════"
    ok "Gate-OS ISO ready: $ISO_OUTPUT"
    ok "Flash with: sudo dd if=$ISO_OUTPUT of=/dev/sdX bs=4M status=progress"
    ok "Or use Ventoy: copy ISO to Ventoy USB drive"
    ok "════════════════════════════════════════"
}

main "$@"
