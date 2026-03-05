#!/usr/bin/env bash
# scripts/load-apparmor-profiles.sh
# ─────────────────────────────────────────────────────────────────────────────
# Load all Gate-OS AppArmor profiles into the kernel's policy cache.
#
# Usage:
#   sudo ./scripts/load-apparmor-profiles.sh [--enforce | --complain] [--no-reload]
#
#   --enforce    Load profiles in enforce mode (default)
#   --complain   Load profiles in complain/audit mode (log-only, no blocking)
#   --no-reload  Skip reloading already-loaded profiles (faster, for CI)
#
# Called automatically by:
#   - scripts/build-iso.sh  (during ISO build chroot)
#   - data/systemd/gateos-api.service  (ExecStartPre)
#   - make apparmor  (developer convenience)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROFILE_DIR="${REPO_ROOT}/profiles/apparmor"

MODE="enforce"
RELOAD=true

# ── Parse arguments ──────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --enforce)   MODE="enforce" ;;
    --complain)  MODE="complain" ;;
    --no-reload) RELOAD=false ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [--enforce | --complain] [--no-reload]" >&2
      exit 1
      ;;
  esac
done

# ── Preflight checks ─────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  echo "Error: This script must be run as root (use sudo)." >&2
  exit 1
fi

if ! command -v apparmor_parser &>/dev/null; then
  echo "Error: apparmor_parser not found. Install with: sudo apt install apparmor" >&2
  exit 1
fi

if ! aa-status --enabled &>/dev/null 2>&1; then
  echo "Warning: AppArmor is not enabled on this kernel. Skipping profile load." >&2
  exit 0
fi

if [[ ! -d "$PROFILE_DIR" ]]; then
  echo "Error: Profile directory not found: $PROFILE_DIR" >&2
  exit 1
fi

# ── Load each profile ─────────────────────────────────────────────────────────
LOADED=0
SKIPPED=0
FAILED=0

shopt -s nullglob
PROFILES=("${PROFILE_DIR}"/gateos-env-*)

if [[ ${#PROFILES[@]} -eq 0 ]]; then
  echo "Warning: No Gate-OS profiles found in ${PROFILE_DIR}" >&2
  exit 0
fi

echo "Gate-OS AppArmor profile loader — mode: ${MODE}"
echo "Profile directory: ${PROFILE_DIR}"
echo "─────────────────────────────────────────"

for profile_path in "${PROFILES[@]}"; do
  profile_name="$(basename "${profile_path}")"

  # Check if already loaded (skip if --no-reload)
  if [[ "$RELOAD" == false ]] && aa-status --json 2>/dev/null | grep -q "\"${profile_name}\""; then
    echo "  SKIP  ${profile_name}  (already loaded)"
    ((SKIPPED++)) || true
    continue
  fi

  # Build apparmor_parser flags
  PARSER_FLAGS=(-r)   # -r = replace (reload if already cached)
  if [[ "$MODE" == "complain" ]]; then
    PARSER_FLAGS+=(-C)  # -C = complain mode
  fi

  if apparmor_parser "${PARSER_FLAGS[@]}" "${profile_path}" 2>/dev/null; then
    echo "  OK    ${profile_name}  [${MODE}]"
    ((LOADED++)) || true
  else
    echo "  FAIL  ${profile_name}" >&2
    ((FAILED++)) || true
  fi
done

echo "─────────────────────────────────────────"
echo "Loaded: ${LOADED}  |  Skipped: ${SKIPPED}  |  Failed: ${FAILED}"

if [[ $FAILED -gt 0 ]]; then
  echo "Error: ${FAILED} profile(s) failed to load." >&2
  exit 1
fi

echo "All profiles loaded successfully."
exit 0
