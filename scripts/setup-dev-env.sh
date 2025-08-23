#!/usr/bin/env bash
set -euo pipefail

echo "[Gate-OS] Dev environment setup" >&2

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python not found. Install Python 3.10+ first." >&2
  exit 1
fi

VENV_DIR=".venv"
if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -e '.[dev]'
echo "Done. Activate with: source $VENV_DIR/bin/activate" >&2
#!/usr/bin/env bash
set -euo pipefail

# Gate-OS Dev Environment Bootstrap (Draft)
# Usage: ./scripts/setup-dev-env.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[Gate-OS] Bootstrapping development environment..."

# 1. Python virtual environment (if Python sources present later)
if command -v python3 >/dev/null 2>&1; then
  if [ ! -d .venv ]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install --upgrade pip >/dev/null 2>&1 || true
  # Placeholder for future dependencies
fi

# 2. Pre-commit (optional future)
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install || true
fi

# 3. Create local hooks dir
mkdir -p .gateos/tmp

# 4. Output manifest schema reference
if [ -f docs/architecture/schemas/environment-manifest.schema.yaml ]; then
  echo "Schema located: docs/architecture/schemas/environment-manifest.schema.yaml"
fi

echo "[Gate-OS] Done. (Future steps: build core manager, run tests, lint)"
