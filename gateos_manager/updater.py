"""
gateos_manager.updater
~~~~~~~~~~~~~~~~~~~~~~~
OTA (Over-The-Air) update mechanism stub.

When fully implemented this module will:
  1. Poll a release feed (GitHub Releases API / custom endpoint) for newer versions.
  2. Download the update package (deb / squashfs delta) to a staging directory.
  3. Verify the integrity (SHA-256 + Ed25519 signature) of the downloaded file.
  4. Apply the update at next boot or immediately (depending on update type).
  5. Support rollback to the previous version if the update fails.

For v1.0.0-beta this module provides:
  - Version comparison helper
  - Update check stub (returns NotImplemented in production)
  - CLI integration point (`gateos check-update`, `gateos apply-update`)

Environment variables:
    GATEOS_UPDATE_FEED   URL of the JSON release feed (default: GitHub Releases API)
    GATEOS_UPDATE_DIR    Staging directory for downloaded packages (default: /var/cache/gateos/updates)
    GATEOS_UPDATE_DISABLE  Set to '1' to disable update checks
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from gateos_manager import __version__

_DEFAULT_FEED = 'https://api.github.com/repos/Ultra-Cube/Gate-OS/releases/latest'
_DEFAULT_UPDATE_DIR = Path(os.getenv('GATEOS_UPDATE_DIR', '/var/cache/gateos/updates'))
_DEFAULT_UPDATE_PUBLIC_KEY = Path(
    os.getenv('GATEOS_UPDATE_PUBLIC_KEY', '/etc/gateos/keys/signing.pub')
)


class UpdateError(Exception):
    """Raised when an update check or application fails."""


@dataclass
class ReleaseInfo:
    """Information about an available release."""

    version: str
    tag: str
    download_url: str
    sha256_url: str
    sig_url: str
    prerelease: bool
    release_notes: str


def _parse_version(v: str) -> tuple[int, ...]:
    """Parse a SemVer-ish string into a comparable tuple.

    Examples:
        "1.0.0-beta" → (1, 0, 0)
        "0.5.0" → (0, 5, 0)
    """
    clean = re.sub(r'[^0-9.]', '', v.lstrip('v'))
    parts = clean.split('.')
    try:
        return tuple(int(p) for p in parts[:3])
    except ValueError:
        return (0, 0, 0)


def is_newer(candidate: str, current: str = __version__) -> bool:
    """Return True if *candidate* version is newer than *current* version."""
    return _parse_version(candidate) > _parse_version(current)


def check_for_update(
    feed_url: str | None = None,
    *,
    timeout: int = 5,
) -> ReleaseInfo | None:
    """Check GitHub Releases for a newer version.

    Returns :class:`ReleaseInfo` if an update is available, ``None`` otherwise.
    Raises :class:`UpdateError` on network or API errors.

    Set ``GATEOS_UPDATE_DISABLE=1`` to disable all update checks.
    """
    if os.getenv('GATEOS_UPDATE_DISABLE') == '1':
        return None

    url = feed_url or os.getenv('GATEOS_UPDATE_FEED', _DEFAULT_FEED)
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': f'Gate-OS/{__version__} updater'},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise UpdateError(f'Update feed unavailable: {exc}') from exc
    except json.JSONDecodeError as exc:
        raise UpdateError(f'Malformed update feed response: {exc}') from exc

    tag = data.get('tag_name', '')
    remote_ver = tag.lstrip('v')

    if not is_newer(remote_ver):
        return None

    # Find the .deb asset
    assets = data.get('assets', [])
    deb_asset = next((a for a in assets if a['name'].endswith('.deb')), None)
    download_url = deb_asset['browser_download_url'] if deb_asset else ''
    sha256_url = next(
        (a['browser_download_url'] for a in assets if a['name'].endswith('.sha256')),
        '',
    )
    sig_url = next(
        (a['browser_download_url'] for a in assets if a['name'].endswith('.sig')),
        '',
    )

    return ReleaseInfo(
        version=remote_ver,
        tag=tag,
        download_url=download_url,
        sha256_url=sha256_url,
        sig_url=sig_url,
        prerelease=data.get('prerelease', False),
        release_notes=data.get('body', ''),
    )


def apply_update(release: ReleaseInfo, *, dry_run: bool = False) -> None:
    """Download and stage an update package for installation.

    In ``dry_run`` mode, only checks that the download URL is accessible.
    Does NOT reboot or apply; call ``schedule_apply()`` for that.

    Raises :class:`UpdateError` on any failure.
    """
    if not release.download_url:
        raise UpdateError('No download URL in release info')

    if dry_run:
        # Just check network reachability
        try:
            req = urllib.request.Request(
                release.download_url,
                method='HEAD',
                headers={'User-Agent': f'Gate-OS/{__version__} updater'},
            )
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.URLError as exc:
            raise UpdateError(f'Download URL inaccessible: {exc}') from exc
        return

    require_verify = os.getenv('GATEOS_UPDATE_REQUIRE_VERIFY') == '1'
    if require_verify and not release.sha256_url:
        raise UpdateError('Secure update mode requires a SHA-256 manifest URL')
    if require_verify and (not release.sig_url or not _DEFAULT_UPDATE_PUBLIC_KEY.exists()):
        raise UpdateError('Secure update mode requires an Ed25519 signature and public key')

    _DEFAULT_UPDATE_DIR.mkdir(parents=True, exist_ok=True)
    dest = _DEFAULT_UPDATE_DIR / f'gateos-{release.version}.deb'

    try:
        urllib.request.urlretrieve(release.download_url, dest)
    except urllib.error.URLError as exc:
        raise UpdateError(f'Download failed: {exc}') from exc

    if release.sha256_url:
        try:
            with urllib.request.urlopen(release.sha256_url, timeout=5) as response:  # nosec B310
                checksum_text = response.read().decode('utf-8')
            expected = next(
                (line.split()[0] for line in checksum_text.splitlines() if line.strip()),
                '',
            ).lower()
            actual = hashlib.sha256(dest.read_bytes()).hexdigest()
            if expected != actual:
                dest.unlink(missing_ok=True)
                raise UpdateError('SHA-256 verification failed')
        except urllib.error.URLError as exc:
            dest.unlink(missing_ok=True)
            raise UpdateError(f'Checksum manifest unavailable: {exc}') from exc
    elif require_verify:
        dest.unlink(missing_ok=True)
        raise UpdateError('Secure update mode requires checksum verification')

    if release.sig_url and require_verify:
        try:
            with urllib.request.urlopen(release.sig_url, timeout=5) as response:  # nosec B310
                signature_text = response.read().decode('utf-8').strip()
            _verify_ed25519(dest, signature_text, _DEFAULT_UPDATE_PUBLIC_KEY)
        except urllib.error.URLError as exc:
            dest.unlink(missing_ok=True)
            raise UpdateError(f'Signature unavailable: {exc}') from exc
        except UpdateError:
            dest.unlink(missing_ok=True)
            raise

    marker = dest.with_suffix('.ready')
    marker.write_text(release.version)


def _verify_ed25519(package: Path, signature_text: str, public_key_path: Path) -> None:
    """Verify a base64-encoded detached Ed25519 signature for *package*."""
    try:
        import base64

        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization

        signature = base64.b64decode(signature_text, validate=True)
        public_key = serialization.load_pem_public_key(public_key_path.read_bytes())
        public_key.verify(signature, package.read_bytes())
    except (ValueError, OSError, InvalidSignature) as exc:
        raise UpdateError('Ed25519 signature verification failed') from exc


def schedule_apply() -> None:
    """Mark the staged update to be applied at next system boot.

    Strategy (in priority order):
      1. Write a systemd drop-in under
         ``/etc/systemd/system/gateos-manager.service.d/apply-update.conf``
         so the service runs ``dpkg -i`` before the next start.
      2. Fall back to a plain flag file at
         ``<GATEOS_UPDATE_DIR>/apply-at-boot.flag`` (read by the
         gate-os-updater.service ExecStartPre script).

    Raises :class:`UpdateError` if no staged package is found.
    """
    import subprocess

    # Find the most recent staged .ready marker
    ready_files = sorted(_DEFAULT_UPDATE_DIR.glob('*.ready'))
    if not ready_files:
        raise UpdateError(
            'No staged update found. Run apply_update() first to download the package.'
        )

    ready_file = ready_files[-1]
    deb_file = ready_file.with_suffix('.deb')

    if not deb_file.exists():
        raise UpdateError(
            f'Staged package missing: {deb_file}. Re-run apply_update() to re-download.'
        )

    # --- Strategy 1: systemd drop-in ---
    dropin_dir = Path('/etc/systemd/system/gateos-manager.service.d')
    try:
        dropin_dir.mkdir(parents=True, exist_ok=True)
        dropin = dropin_dir / 'apply-update.conf'
        dropin.write_text(
            '[Service]\n'
            f'ExecStartPre=/usr/bin/dpkg -i {deb_file}\n'
            'ExecStartPre=/bin/rm -f '
            f'{deb_file} {ready_file} {dropin_dir}/apply-update.conf\n'
        )
        subprocess.run(
            ['systemctl', 'daemon-reload'],
            check=False,
            capture_output=True,
            timeout=5,
        )
        return
    except PermissionError:
        pass  # fallthrough to flag file strategy

    # --- Strategy 2: flag file ---
    _DEFAULT_UPDATE_DIR.mkdir(parents=True, exist_ok=True)
    flag = _DEFAULT_UPDATE_DIR / 'apply-at-boot.flag'
    flag.write_text(str(deb_file))
