"""Extended updater tests — covering previously uncovered lines (80% → 95%+).

Covers:
  - apply_update() dry_run=False real download path
  - apply_update() no download_url → UpdateError
  - apply_update() dry_run HEAD request failure
  - schedule_apply() no .ready files → UpdateError
  - schedule_apply() missing .deb → UpdateError
  - schedule_apply() strategy 1: systemd drop-in + daemon-reload
  - schedule_apply() strategy 2: PermissionError fallback → flag file
  - check_for_update() GATEOS_UPDATE_DISABLE env var
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

import gateos_manager.updater as _upd

# Convenience aliases — always fetched from the live module object so they
# remain valid even after importlib.reload() in other test files.
def _UpdateError():
    return _upd.UpdateError

def _apply_update(*a, **kw):
    return _upd.apply_update(*a, **kw)

def _check_for_update(*a, **kw):
    return _upd.check_for_update(*a, **kw)

def _schedule_apply(*a, **kw):
    return _upd.schedule_apply(*a, **kw)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_release(version: str = "2.0.0") -> _upd.ReleaseInfo:
    return _upd.ReleaseInfo(
        version=version,
        tag=f"v{version}",
        download_url=f"https://example.com/gateos-{version}.deb",
        sha256_url="",
        sig_url="",
        prerelease=False,
        release_notes="",
    )


# ─────────────────────────────────────────────────────────────────────────────
# check_for_update — environment variable disable
# ─────────────────────────────────────────────────────────────────────────────

def test_check_update_disabled_env(monkeypatch):
    """GATEOS_UPDATE_DISABLE=1 should return None without any network call."""
    monkeypatch.setenv("GATEOS_UPDATE_DISABLE", "1")
    with patch("urllib.request.urlopen") as mock_open:
        result = _check_for_update()
    assert result is None
    mock_open.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# apply_update — error cases
# ─────────────────────────────────────────────────────────────────────────────

def test_apply_update_no_download_url():
    """Missing download_url must raise UpdateError before any network call."""
    rel = _make_release()
    rel.download_url = ""
    with pytest.raises(_UpdateError(), match="No download URL"):
        _apply_update(rel)


def test_apply_update_dry_run_url_inaccessible():
    """dry_run=True should raise UpdateError when HEAD request fails."""
    import urllib.error
    rel = _make_release()
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
        with pytest.raises(_UpdateError(), match="inaccessible"):
            _apply_update(rel, dry_run=True)


def test_apply_update_dry_run_success():
    """dry_run=True should succeed when HEAD returns 200."""
    rel = _make_release()
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        _apply_update(rel, dry_run=True)  # should not raise


# ─────────────────────────────────────────────────────────────────────────────
# apply_update — real download (dry_run=False)
# ─────────────────────────────────────────────────────────────────────────────

def test_apply_update_real_download_success(tmp_path):
    """dry_run=False should download the deb and write a .ready marker."""
    rel = _make_release("2.0.0")

    with patch("gateos_manager.updater._DEFAULT_UPDATE_DIR", tmp_path), \
         patch("gateos_manager.updater.urllib.request.urlretrieve") as mock_retrieve:
        _apply_update(rel, dry_run=False)

    dest = tmp_path / "gateos-2.0.0.deb"
    marker = tmp_path / "gateos-2.0.0.ready"

    mock_retrieve.assert_called_once_with(rel.download_url, dest)
    assert marker.exists()
    assert marker.read_text() == "2.0.0"


def test_apply_update_real_download_url_error(tmp_path):
    """Network error during download must raise UpdateError."""
    import urllib.error
    rel = _make_release("2.0.0")

    with patch("gateos_manager.updater._DEFAULT_UPDATE_DIR", tmp_path), \
         patch("gateos_manager.updater.urllib.request.urlretrieve",
               side_effect=urllib.error.URLError("timeout")):
        with pytest.raises(_UpdateError(), match="Download failed"):
            _apply_update(rel, dry_run=False)


# ─────────────────────────────────────────────────────────────────────────────
# schedule_apply — precondition failures
# ─────────────────────────────────────────────────────────────────────────────

def test_schedule_apply_no_ready_files(tmp_path):
    """Empty staging dir must raise UpdateError."""
    with patch("gateos_manager.updater._DEFAULT_UPDATE_DIR", tmp_path):
        with pytest.raises(_UpdateError(), match="No staged update"):
            _schedule_apply()


def test_schedule_apply_missing_deb(tmp_path):
    """A .ready marker without a matching .deb must raise UpdateError."""
    ready = tmp_path / "gateos-2.0.0.ready"
    ready.write_text("2.0.0")
    # No corresponding .deb in tmp_path

    with patch("gateos_manager.updater._DEFAULT_UPDATE_DIR", tmp_path):
        with pytest.raises(_UpdateError(), match="Staged package missing"):
            _schedule_apply()


# ─────────────────────────────────────────────────────────────────────────────
# schedule_apply — strategy 1: systemd drop-in
# ─────────────────────────────────────────────────────────────────────────────

def test_schedule_apply_strategy1_systemd(tmp_path):
    """Happy path: write systemd drop-in and call daemon-reload."""
    # Create staged .deb + .ready
    ready = tmp_path / "gateos-2.0.0.ready"
    ready.write_text("2.0.0")
    deb = tmp_path / "gateos-2.0.0.deb"
    deb.write_bytes(b"fake deb")

    dropin_dir = tmp_path / "etc_systemd"

    real_Path = Path

    def fake_path(s):
        if s == "/etc/systemd/system/gateos-manager.service.d":
            return dropin_dir
        return real_Path(s)

    with patch("gateos_manager.updater._DEFAULT_UPDATE_DIR", tmp_path), \
         patch("gateos_manager.updater.Path", side_effect=fake_path), \
         patch("subprocess.run") as mock_run:
        _schedule_apply()

    conf = dropin_dir / "apply-update.conf"
    assert conf.exists()
    assert "dpkg -i" in conf.read_text()
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0] == ["systemctl", "daemon-reload"]


# ─────────────────────────────────────────────────────────────────────────────
# schedule_apply — strategy 2: PermissionError fallback → flag file
# ─────────────────────────────────────────────────────────────────────────────

def test_schedule_apply_strategy2_flag_file(tmp_path):
    """PermissionError on drop-in mkdir → fall back to flag file."""
    ready = tmp_path / "gateos-2.0.0.ready"
    ready.write_text("2.0.0")
    deb = tmp_path / "gateos-2.0.0.deb"
    deb.write_bytes(b"fake deb")

    dropin_dir = tmp_path / "no_perms_dir"

    real_Path = Path

    def fake_path(s):
        if s == "/etc/systemd/system/gateos-manager.service.d":
            return dropin_dir
        return real_Path(s)

    real_mkdir = Path.mkdir

    def raising_mkdir(self, *args, **kwargs):
        if self == dropin_dir:
            raise PermissionError("no write access to /etc")
        return real_mkdir(self, *args, **kwargs)

    with patch("gateos_manager.updater._DEFAULT_UPDATE_DIR", tmp_path), \
         patch("gateos_manager.updater.Path", side_effect=fake_path), \
         patch.object(Path, "mkdir", raising_mkdir):
        _schedule_apply()

    flag = tmp_path / "apply-at-boot.flag"
    assert flag.exists()
    assert str(deb) in flag.read_text()
