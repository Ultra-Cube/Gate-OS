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

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from gateos_manager import __version__

_DEFAULT_FEED = "https://api.github.com/repos/Ultra-Cube/Gate-OS/releases/latest"
_DEFAULT_UPDATE_DIR = Path(os.getenv("GATEOS_UPDATE_DIR", "/var/cache/gateos/updates"))


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
    clean = re.sub(r"[^0-9.]", "", v.lstrip("v"))
    parts = clean.split(".")
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
) -> Optional[ReleaseInfo]:
    """Check GitHub Releases for a newer version.

    Returns :class:`ReleaseInfo` if an update is available, ``None`` otherwise.
    Raises :class:`UpdateError` on network or API errors.

    Set ``GATEOS_UPDATE_DISABLE=1`` to disable all update checks.
    """
    if os.getenv("GATEOS_UPDATE_DISABLE") == "1":
        return None

    url = feed_url or os.getenv("GATEOS_UPDATE_FEED", _DEFAULT_FEED)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"Gate-OS/{__version__} updater"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise UpdateError(f"Update feed unavailable: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise UpdateError(f"Malformed update feed response: {exc}") from exc

    tag = data.get("tag_name", "")
    remote_ver = tag.lstrip("v")

    if not is_newer(remote_ver):
        return None

    # Find the .deb asset
    assets = data.get("assets", [])
    deb_asset = next((a for a in assets if a["name"].endswith(".deb")), None)
    download_url = deb_asset["browser_download_url"] if deb_asset else ""
    sha256_url = next(
        (a["browser_download_url"] for a in assets if a["name"].endswith(".sha256")),
        "",
    )
    sig_url = next(
        (a["browser_download_url"] for a in assets if a["name"].endswith(".sig")),
        "",
    )

    return ReleaseInfo(
        version=remote_ver,
        tag=tag,
        download_url=download_url,
        sha256_url=sha256_url,
        sig_url=sig_url,
        prerelease=data.get("prerelease", False),
        release_notes=data.get("body", ""),
    )


def apply_update(release: ReleaseInfo, *, dry_run: bool = False) -> None:
    """Download and stage an update package for installation.

    In ``dry_run`` mode, only checks that the download URL is accessible.
    Does NOT reboot or apply; call ``schedule_apply()`` for that.

    Raises :class:`UpdateError` on any failure.
    """
    if not release.download_url:
        raise UpdateError("No download URL in release info")

    if dry_run:
        # Just check network reachability
        try:
            req = urllib.request.Request(
                release.download_url,
                method="HEAD",
                headers={"User-Agent": f"Gate-OS/{__version__} updater"},
            )
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.URLError as exc:
            raise UpdateError(f"Download URL inaccessible: {exc}") from exc
        return

    _DEFAULT_UPDATE_DIR.mkdir(parents=True, exist_ok=True)
    dest = _DEFAULT_UPDATE_DIR / f"gateos-{release.version}.deb"

    try:
        urllib.request.urlretrieve(release.download_url, dest)
    except urllib.error.URLError as exc:
        raise UpdateError(f"Download failed: {exc}") from exc

    # TODO: verify SHA-256 and Ed25519 signature before marking ready
    marker = dest.with_suffix(".ready")
    marker.write_text(release.version)


def schedule_apply() -> None:
    """Mark the staged update to be applied at next system boot.

    Creates a systemd drop-in or a flag file that the gate-os-updater.service
    references on startup.  Not yet implemented — stub only.
    """
    raise NotImplementedError(
        "schedule_apply() is a stub in v1.0.0-beta. "
        "Manual installation: sudo dpkg -i /var/cache/gateos/updates/gateos-*.deb"
    )
