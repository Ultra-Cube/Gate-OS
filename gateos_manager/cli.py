"""CLI entrypoints for Gate-OS manager (draft)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .manifest.loader import ManifestValidationError, load_manifest


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gateos", description="Gate-OS Manager Utilities (draft)")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate one or more environment manifest files")
    v.add_argument("paths", nargs="+", help="Manifest file paths (YAML)")
    v.add_argument(
        "--schema",
        default="docs/architecture/schemas/environment-manifest.schema.yaml",
        help="Schema path (YAML)",
    )
    a = sub.add_parser("api", help="Run local control API server (experimental)")
    a.add_argument("--host", default="127.0.0.1", help="Bind host")
    a.add_argument("--port", type=int, default=8088, help="Bind port")
    a.add_argument("--schema", default="docs/architecture/schemas/environment-manifest.schema.yaml", help="Schema for environment listing")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "validate":
        errors = 0
        for raw in args.paths:
            path = Path(raw)
            try:
                load_manifest(path, Path(args.schema))
                print(f"OK: {path}")
            except ManifestValidationError as e:  # noqa: PERF203 minimal now
                errors += 1
                print(f"FAIL: {path}: {e}", file=sys.stderr)
        return 1 if errors else 0
    if args.cmd == "api":
        try:
            from .api.server import run_server
        except ImportError as e:  # pragma: no cover
            print("FastAPI not installed. Install with 'pip install .[api]'", file=sys.stderr)
            return 1
        run_server(host=args.host, port=args.port, schema_path=Path(args.schema))
        return 0
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
