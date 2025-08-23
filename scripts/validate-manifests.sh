#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEMA="${ROOT}/docs/architecture/schemas/environment-manifest.schema.yaml"
EXAMPLES_DIR="${ROOT}/examples/environments"

if ! command -v python >/dev/null 2>&1; then
  echo "Python not found" >&2
  exit 1
fi

if [ ! -f "$SCHEMA" ]; then
  echo "Schema missing: $SCHEMA" >&2
  exit 1
fi

MANIFESTS=$(ls "$EXAMPLES_DIR"/*.yaml 2>/dev/null || true)
if [ -z "$MANIFESTS" ]; then
  echo "No manifests found in $EXAMPLES_DIR" >&2
  exit 1
fi

echo "Validating manifests against schema..." >&2
python -m gateos_manager.cli validate $MANIFESTS --schema "$SCHEMA"
echo "All manifests valid." >&2
