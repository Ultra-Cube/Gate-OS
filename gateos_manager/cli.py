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
    t = sub.add_parser("gen-token", help="Generate and print a random API token")
    t.add_argument("--length", type=int, default=32, help="Token length")

    s = sub.add_parser("sign", help="Sign a manifest file with the Ed25519 private key")
    s.add_argument("manifest", help="Path to the manifest YAML file")
    s.add_argument("--key-dir", default=None, help="Directory containing signing.key (default: /etc/gateos/keys/)")

    vf = sub.add_parser("verify", help="Verify the Ed25519 signature of a manifest file")
    vf.add_argument("manifest", help="Path to the manifest YAML file")
    vf.add_argument("--sig", default=None, help="Signature file path (default: <manifest>.sig)")
    vf.add_argument("--key-dir", default=None, help="Directory containing signing.pub (default: /etc/gateos/keys/)")

    kg = sub.add_parser("gen-keypair", help="Generate a new Ed25519 signing keypair (dev/key-rotation use only)")
    kg.add_argument("--key-dir", default=None, help="Output directory for the key pair")

    cu = sub.add_parser("check-update", help="Check GitHub Releases for a newer Gate-OS version")
    cu.add_argument("--feed", default=None, help="Custom release feed URL")
    cu.add_argument("--include-prerelease", action="store_true", help="Include pre-release versions")

    au = sub.add_parser("apply-update", help="Download and stage a Gate-OS update (dry-run by default)")
    au.add_argument("--dry-run", action="store_true", default=True, help="Check download URL without downloading (default: True)")
    au.add_argument("--yes", action="store_true", help="Actually download the update package")

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
    if args.cmd == "gen-token":
        import secrets, string
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(args.length))
        print(token)
        return 0
    if args.cmd == "sign":
        from .security.signing import sign, SigningError
        from pathlib import Path as _Path
        try:
            key_dir = _Path(args.key_dir) if args.key_dir else None
            sig_path = sign(args.manifest, key_dir=key_dir)
            print(f"Signed: {args.manifest}  →  {sig_path}")
            return 0
        except SigningError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    if args.cmd == "verify":
        from .security.signing import verify, SigningError
        from pathlib import Path as _Path
        try:
            key_dir = _Path(args.key_dir) if args.key_dir else None
            verify(args.manifest, args.sig, key_dir=key_dir)
            print(f"OK: signature valid for {args.manifest}")
            return 0
        except SigningError as e:
            print(f"INVALID: {e}", file=sys.stderr)
            return 1
    if args.cmd == "gen-keypair":
        from .security.signing import generate_keypair, SigningError
        from pathlib import Path as _Path
        try:
            key_dir = _Path(args.key_dir) if args.key_dir else None
            priv, pub = generate_keypair(key_dir)
            print(f"Private key: {priv}")
            print(f"Public key:  {pub}")
            return 0
        except SigningError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    if args.cmd == "check-update":
        from .updater import check_for_update, UpdateError
        from gateos_manager import __version__ as _ver
        try:
            release = check_for_update(args.feed)
            if release is None:
                print(f"Gate-OS is up to date (v{_ver})")
                return 0
            if release.prerelease and not args.include_prerelease:
                print(f"Pre-release v{release.version} available (use --include-prerelease to see)")
                return 0
            print(f"Update available: v{release.version}")
            print(f"  Download: {release.download_url}")
            if release.release_notes:
                print(f"  Release notes:\n{release.release_notes[:500]}")
            return 0
        except UpdateError as e:
            print(f"Update check failed: {e}", file=sys.stderr)
            return 1
    if args.cmd == "apply-update":
        from .updater import check_for_update, apply_update, UpdateError
        dry_run = not args.yes
        try:
            release = check_for_update()
            if release is None:
                print("Already up to date.")
                return 0
            apply_update(release, dry_run=dry_run)
            if dry_run:
                print(f"Dry-run OK: v{release.version} download URL is accessible. Use --yes to download.")
            else:
                print(f"Downloaded v{release.version} to staging. Reboot to apply.")
            return 0
        except UpdateError as e:
            print(f"Update failed: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
