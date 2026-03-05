#!/usr/bin/env bash
set -euo pipefail

echo "[dev-check] Lint (ruff)"
ruff check gateos_manager

echo "[dev-check] YAML lint"
if command -v yamllint >/dev/null; then
  yamllint .
else
  echo "yamllint not installed (skipping)"
fi

echo "[dev-check] Markdown lint"
if command -v markdownlint-cli2 >/dev/null; then
  markdownlint-cli2 "**/*.md" "#node_modules"
else
  echo "markdownlint not installed (skipping)"
fi

echo "[dev-check] Tests"
pytest -q

echo "[dev-check] Manifest validation"
if [[ -f docs/architecture/schemas/environment-manifest.schema.yaml ]]; then
  gateos validate examples/environments/*.yaml --schema docs/architecture/schemas/environment-manifest.schema.yaml || true
fi

echo "[dev-check] DONE"