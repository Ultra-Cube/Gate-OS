#!/usr/bin/env bash
set -euo pipefail

echo "[Gate-OS] Installing Deepin Desktop Environment (DDE) (placeholder)" >&2
echo "This script will attempt to install DDE packages. Review before running in production." >&2

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (apt operations)" >&2
  exit 1
fi

apt update
apt install -y dde-session-ui dde-file-manager || echo "DDE minimal packages not found on this base; adjust repository sources." >&2

echo "Install complete. Select DDE session at login manager." >&2