#!/usr/bin/env bash
# install-dde.sh — Install Deepin Desktop Environment on Ubuntu 22.04 / 24.04
# Usage: sudo bash scripts/install-dde.sh
set -euo pipefail

UBUNTU_CODENAME="$(lsb_release -cs 2>/dev/null || echo unknown)"
DDE_PPA_22="ppa:ubuntudde-dev/stable"
DDE_PPA_24="ppa:ubuntudde-dev/noble"  # Noble = Ubuntu 24.04

echo "[Gate-OS] Installing Deepin Desktop Environment on Ubuntu ${UBUNTU_CODENAME}" >&2

if [[ $EUID -ne 0 ]]; then
  echo "ERROR: Please run as root (sudo is required for apt operations)." >&2
  exit 1
fi

# Ensure prerequisites
apt-get update -qq
apt-get install -y --no-install-recommends software-properties-common lsb-release

case "${UBUNTU_CODENAME}" in
  noble | oracular)
    echo "[Gate-OS] Adding UbuntuDDE PPA for Noble (24.04)..." >&2
    add-apt-repository -y "${DDE_PPA_24}"
    ;;
  jammy | kinetic | lunar | mantic)
    echo "[Gate-OS] Adding UbuntuDDE PPA for Jammy (22.04/23.x)..." >&2
    add-apt-repository -y "${DDE_PPA_22}"
    ;;
  *)
    echo "WARNING: Unrecognised Ubuntu release '${UBUNTU_CODENAME}'." >&2
    echo "         Attempting stable PPA anyway — adjust if packages fail." >&2
    add-apt-repository -y "${DDE_PPA_22}"
    ;;
esac

apt-get update -qq

# Core DDE packages
apt-get install -y \
  dde-session-ui \
  dde-file-manager \
  dde-control-center \
  dde-launcher \
  dde-dock \
  startdde \
  || {
    echo "WARNING: Some DDE packages not found — installing minimal set." >&2
    apt-get install -y dde-session-ui dde-file-manager || true
  }

# Check for Gate-OS DDE panel Python SDK
if python3 -c "import dde_plugin_manager" 2>/dev/null; then
  echo "[Gate-OS] dde_plugin_manager Python SDK is available." >&2
else
  echo "[Gate-OS] dde_plugin_manager not found; Gate-OS DDE panel will run in stub mode." >&2
  echo "          Install the Deepin Python plugin SDK from the UbuntuDDE PPA when available." >&2
fi

echo "[Gate-OS] DDE installation complete." >&2
echo "          Select 'Deepin' session at your login manager (SDDM/GDM/LightDM)." >&2

echo "Install complete. Select DDE session at login manager." >&2