#!/usr/bin/env bash
set -euo pipefail

# Gate-OS Dev Environment Setup
# Usage: ./scripts/setup-dev-env.sh
# Tested on: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[Gate-OS] Setting up development environment..."

# ── 1. Ensure Python 3.10+ ───────────────────────────────────────────────────
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[Gate-OS] Python 3 not found. Attempting install via apt..." >&2
  if command -v apt >/dev/null 2>&1; then
    sudo apt update -qq && sudo apt install -y python3 python3-venv python3-pip
    PYTHON_BIN=python3
  else
    echo "[Gate-OS] ERROR: Install Python 3.10+ manually then re-run." >&2
    exit 1
  fi
fi

PY_MINOR=$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.minor)')
if [[ "$PY_MINOR" -lt 10 ]]; then
  echo "[Gate-OS] ERROR: Python 3.10+ required (found 3.$PY_MINOR)." >&2
  exit 1
fi
echo "[Gate-OS] Using: $("$PYTHON_BIN" --version)"

# ── 2. Create virtualenv ─────────────────────────────────────────────────────
VENV_DIR=".venv"
if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  echo "[Gate-OS] Created virtualenv at $VENV_DIR"
else
  echo "[Gate-OS] Virtualenv already exists at $VENV_DIR"
fi

# ── 3. Install dependencies ──────────────────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip -q
pip install -e '.[dev]' -q
echo "[Gate-OS] Dependencies installed."

# ── 4. Optional: pre-commit hooks ───────────────────────────────────────────
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install --quiet || true
  echo "[Gate-OS] pre-commit hooks installed."
fi

# ── 5. Create local runtime dirs ────────────────────────────────────────────
mkdir -p .gateos/tmp

# ── 6. Verify setup ─────────────────────────────────────────────────────────
echo ""
echo "[Gate-OS] Verifying installation..."
python -m pytest tests/ -q --tb=no 2>&1 | tail -3
echo ""
echo "[Gate-OS] ✅ Done! Next steps:"
echo "  source $VENV_DIR/bin/activate"
echo "  make test        # run all tests"
echo "  make lint        # run ruff linter"
echo "  make validate    # validate manifests"
echo "  make api         # start Control API on :8088"
