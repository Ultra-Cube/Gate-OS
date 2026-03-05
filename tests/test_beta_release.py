"""Tests for Phase 8 — Beta Release / OTA Update mechanism.

Covers:
- Version comparison helper (is_newer, _parse_version)
- check_for_update() — mocked GitHub API responses
- apply_update() dry-run mode
- apply_update() download mode (mocked urllib)
- CLI: gateos check-update, gateos apply-update
- UpdateError propagation on network failure
- GATEOS_UPDATE_DISABLE env var
- schedule_apply() raises UpdateError when no staged package exists
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import urllib.error

import pytest


# ──────────────────────────────────────────────────────────────────────────
# Version comparison tests
# ──────────────────────────────────────────────────────────────────────────

def test_parse_version_semver():
    from gateos_manager.updater import _parse_version
    assert _parse_version("1.2.3") == (1, 2, 3)
    assert _parse_version("v0.5.0") == (0, 5, 0)
    assert _parse_version("1.0.0-beta") == (1, 0, 0)


def test_parse_version_invalid_returns_zeros():
    from gateos_manager.updater import _parse_version
    assert _parse_version("") == (0, 0, 0)
    assert _parse_version("invalid") == (0, 0, 0)


def test_is_newer_true():
    from gateos_manager.updater import is_newer
    assert is_newer("1.0.0", current="0.5.0") is True
    assert is_newer("0.6.0", current="0.5.0") is True


def test_is_newer_false():
    from gateos_manager.updater import is_newer
    assert is_newer("0.5.0", current="0.5.0") is False
    assert is_newer("0.4.9", current="0.5.0") is False


def test_is_newer_uses_current_version():
    """is_newer(candidate) without explicit current uses __version__."""
    from gateos_manager.updater import is_newer
    from gateos_manager import __version__
    # candidate older than current version should be False
    assert is_newer("0.0.1") is False


# ──────────────────────────────────────────────────────────────────────────
# check_for_update tests
# ──────────────────────────────────────────────────────────────────────────

def _fake_response(data: dict) -> MagicMock:
    resp = MagicMock()
    resp.read.return_value = json.dumps(data).encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


_MOCK_RELEASE = {
    "tag_name": "v99.0.0",
    "prerelease": False,
    "body": "New features and bug fixes.",
    "assets": [
        {"name": "gateos-99.0.0.deb", "browser_download_url": "https://example.com/gateos.deb"},
        {"name": "gateos-99.0.0.sha256", "browser_download_url": "https://example.com/gateos.sha256"},
        {"name": "gateos-99.0.0.sig", "browser_download_url": "https://example.com/gateos.sig"},
    ],
}


def test_check_for_update_returns_release_info():
    from gateos_manager.updater import check_for_update, ReleaseInfo
    with patch("urllib.request.urlopen", return_value=_fake_response(_MOCK_RELEASE)):
        release = check_for_update()
    assert release is not None
    assert isinstance(release, ReleaseInfo)
    assert release.version == "99.0.0"
    assert release.prerelease is False
    assert "gateos.deb" in release.download_url


def test_check_for_update_no_newer_returns_none():
    from gateos_manager.updater import check_for_update
    old_release = dict(_MOCK_RELEASE, tag_name="v0.0.1")
    with patch("urllib.request.urlopen", return_value=_fake_response(old_release)):
        result = check_for_update()
    assert result is None


def test_check_for_update_network_error_raises():
    from gateos_manager.updater import check_for_update, UpdateError
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        with pytest.raises(UpdateError, match="unavailable"):
            check_for_update()


def test_check_for_update_malformed_json_raises():
    from gateos_manager.updater import check_for_update, UpdateError
    bad_resp = MagicMock()
    bad_resp.read.return_value = b"not-json"
    bad_resp.__enter__ = lambda s: s
    bad_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=bad_resp):
        with pytest.raises(UpdateError, match="Malformed"):
            check_for_update()


def test_check_for_update_disabled_by_env(monkeypatch):
    from gateos_manager.updater import check_for_update
    monkeypatch.setenv("GATEOS_UPDATE_DISABLE", "1")
    # Should return None without making any network call
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = check_for_update()
    assert result is None
    mock_urlopen.assert_not_called()


def test_check_for_update_prerelease_flag():
    from gateos_manager.updater import check_for_update, ReleaseInfo
    pre = dict(_MOCK_RELEASE, prerelease=True)
    with patch("urllib.request.urlopen", return_value=_fake_response(pre)):
        release = check_for_update()
    assert release is not None
    assert release.prerelease is True


# ──────────────────────────────────────────────────────────────────────────
# apply_update tests
# ──────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def mock_release():
    from gateos_manager.updater import ReleaseInfo
    return ReleaseInfo(
        version="99.0.0",
        tag="v99.0.0",
        download_url="https://example.com/gateos-99.0.0.deb",
        sha256_url="https://example.com/gateos-99.0.0.sha256",
        sig_url="https://example.com/gateos-99.0.0.sig",
        prerelease=False,
        release_notes="Lots of fixes.",
    )


def test_apply_update_dry_run_checks_url(mock_release):
    from gateos_manager.updater import apply_update
    head_resp = MagicMock()
    head_resp.__enter__ = lambda s: s
    head_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=head_resp) as mock_open_:
        apply_update(mock_release, dry_run=True)
    mock_open_.assert_called_once()


def test_apply_update_dry_run_network_error_raises(mock_release):
    from gateos_manager.updater import apply_update, UpdateError
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        with pytest.raises(UpdateError, match="inaccessible"):
            apply_update(mock_release, dry_run=True)


def test_apply_update_no_download_url_raises():
    from gateos_manager.updater import apply_update, UpdateError, ReleaseInfo
    empty = ReleaseInfo("99.0.0", "v99.0.0", "", "", "", False, "")
    with pytest.raises(UpdateError, match="No download URL"):
        apply_update(empty, dry_run=False)


def test_apply_update_download_creates_ready_marker(mock_release, tmp_path, monkeypatch):
    from gateos_manager import updater
    monkeypatch.setattr(updater, "_DEFAULT_UPDATE_DIR", tmp_path)
    with patch("urllib.request.urlretrieve"):
        updater.apply_update(mock_release, dry_run=False)
    marker = tmp_path / "gateos-99.0.0.ready"
    assert marker.exists()
    assert marker.read_text() == "99.0.0"


# ──────────────────────────────────────────────────────────────────────────
# schedule_apply stub test
# ──────────────────────────────────────────────────────────────────────────

def test_schedule_apply_raises_update_error_when_no_staged_package():
    """schedule_apply() raises UpdateError when no staged .ready file exists."""
    from gateos_manager.updater import schedule_apply, UpdateError
    import tempfile, os
    # Point update dir at empty temp directory so no .ready files exist
    with tempfile.TemporaryDirectory() as d:
        with patch.dict(os.environ, {"GATEOS_UPDATE_DIR": d}):
            # Re-import to pick up the new env var
            import importlib
            import gateos_manager.updater as _upd
            importlib.reload(_upd)
            with pytest.raises(_upd.UpdateError, match="No staged update"):
                _upd.schedule_apply()
        # Restore
        importlib.reload(_upd)


# ──────────────────────────────────────────────────────────────────────────
# CLI tests
# ──────────────────────────────────────────────────────────────────────────

def test_cli_check_update_up_to_date(capsys, monkeypatch):
    from gateos_manager.cli import main
    from gateos_manager import updater as _upd
    monkeypatch.setattr(_upd, "check_for_update", lambda feed=None, timeout=5: None)
    rc = main(["check-update"])
    assert rc == 0
    assert "up to date" in capsys.readouterr().out


def test_cli_check_update_available(capsys, monkeypatch):
    from gateos_manager.cli import main
    from gateos_manager import updater as _upd
    from gateos_manager.updater import ReleaseInfo
    fake = ReleaseInfo("99.0.0", "v99.0.0", "https://ex.com/pkg.deb", "", "", False, "Big update")
    monkeypatch.setattr(_upd, "check_for_update", lambda feed=None, timeout=5: fake)
    rc = main(["check-update"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "99.0.0" in out


def test_cli_check_update_network_error(capsys, monkeypatch):
    from gateos_manager.cli import main
    from gateos_manager import updater as _upd
    from gateos_manager.updater import UpdateError
    monkeypatch.setattr(_upd, "check_for_update", lambda feed=None, timeout=5: (_ for _ in ()).throw(UpdateError("timeout")))
    rc = main(["check-update"])
    assert rc == 1
    assert "failed" in capsys.readouterr().err


def test_cli_apply_update_dry_run(capsys, monkeypatch):
    from gateos_manager.cli import main
    from gateos_manager import updater as _upd
    from gateos_manager.updater import ReleaseInfo
    fake = ReleaseInfo("99.0.0", "v99.0.0", "https://ex.com/pkg.deb", "", "", False, "")
    monkeypatch.setattr(_upd, "check_for_update", lambda: fake)
    monkeypatch.setattr(_upd, "apply_update", lambda r, dry_run=True: None)
    rc = main(["apply-update"])
    assert rc == 0
