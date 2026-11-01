#!/usr/bin/env bash
# Bounded QEMU boot smoke test for Gate-OS ISO artifacts.
set -euo pipefail

ISO_PATH="${1:-}"
TIMEOUT_SECONDS="${QEMU_BOOT_TIMEOUT:-90}"
OUTPUT_DIR="${QEMU_BOOT_OUTPUT_DIR:-dist/qemu-boot}"
FIRMWARE_ARGS=()

if [[ "${2:-}" == "--uefi" ]]; then
    for candidate in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd; do
        if [[ -f "$candidate" ]]; then
            FIRMWARE_ARGS=(-bios "$candidate")
            break
        fi
    done
    [[ ${#FIRMWARE_ARGS[@]} -gt 0 ]] || { echo "OVMF firmware is required for --uefi" >&2; exit 2; }
fi

if [[ -z "$ISO_PATH" || ! -f "$ISO_PATH" ]]; then
    echo "Usage: $0 PATH_TO_ISO" >&2
    exit 2
fi
command -v qemu-system-x86_64 >/dev/null || { echo "qemu-system-x86_64 is required" >&2; exit 2; }
mkdir -p "$OUTPUT_DIR"
LOG_PATH="$OUTPUT_DIR/$(basename "$ISO_PATH").serial.log"

set +e
timeout --foreground "${TIMEOUT_SECONDS}s" qemu-system-x86_64 \
    -machine q35 \
    -m 2048 \
    -smp 2 \
    -accel tcg \
    -cdrom "$ISO_PATH" "${FIRMWARE_ARGS[@]}" \
    -boot d \
    -nographic \
    -serial stdio \
    >"$LOG_PATH" 2>&1
QEMU_STATUS=$?
set -e

# timeout(124) is acceptable for a live ISO that remains at its boot menu;
# startup crashes and command failures are not.
if [[ "$QEMU_STATUS" -ne 0 && "$QEMU_STATUS" -ne 124 ]]; then
    echo "QEMU failed with status $QEMU_STATUS; see $LOG_PATH" >&2
    exit "$QEMU_STATUS"
fi
if grep -Eqi "kernel panic|fatal|no bootable device" "$LOG_PATH"; then
    echo "QEMU boot log contains a fatal marker; see $LOG_PATH" >&2
    exit 1
fi
echo "QEMU boot smoke test completed; serial log: $LOG_PATH"
