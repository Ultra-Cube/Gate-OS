#!/usr/bin/env bash
# Ensure this script is executable: chmod +x scripts/release.sh
set -euo pipefail

if [[ -n "${DEBUG:-}" ]]; then
  set -x
fi

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

version_file="pyproject.toml"
version="$(grep '^version = ' "$version_file" | head -1 | cut -d '"' -f2)"

echo "Preparing release v$version"

# Ensure clean git status
if [[ -n $(git status --porcelain) ]]; then
  echo "Git working tree not clean. Commit or stash changes first." >&2
  exit 1
fi

echo "Running tests..."
if hatch -h >/dev/null 2>&1; then
  hatch run test || { echo "Tests failed" >&2; exit 1; }
else
  python -m pytest -q || { echo "Tests failed" >&2; exit 1; }
fi

echo "Generating distribution artifacts..."
if hatch -h >/dev/null 2>&1; then
  hatch build
else
  python -m build
fi

git tag -a "v$version" -m "Release v$version"
git push origin "v$version"

echo "Release v$version tagged and pushed."