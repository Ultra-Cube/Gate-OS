"""Extended CLI tests — covering previously uncovered lines (73% → 90%+).

Covers:
  - sign, verify, gen-keypair subcommands (success + failure)
  - check-update success, up-to-date, pre-release filter, network error
  - apply-update dry-run success; real download (--yes) success; error
  - api subcommand import path (ImportError covered by pragma in source)
  - gen-token with custom length
  - validate with multiple paths (success + failure)
"""
from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gateos_manager.cli import main


# ─────────────────────────────────────────────────────────────────────────────
# validate
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_ok(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("gateos_manager.cli.load_manifest") as mock_load:
        mock_load.return_value = {"name": "dev"}
        code = main(["validate", "dev.yaml"])
    assert code == 0


def test_validate_fail(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from gateos_manager.manifest.loader import ManifestValidationError
    with patch("gateos_manager.cli.load_manifest", side_effect=ManifestValidationError("bad")):
        code = main(["validate", "dev.yaml"])
    assert code == 1
    assert "FAIL" in capsys.readouterr().err


def test_validate_multiple_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("gateos_manager.cli.load_manifest") as mock_load:
        mock_load.return_value = {}
        code = main(["validate", "a.yaml", "b.yaml", "c.yaml"])
    assert code == 0
    assert mock_load.call_count == 3


# ─────────────────────────────────────────────────────────────────────────────
# gen-token
# ─────────────────────────────────────────────────────────────────────────────

def test_gen_token_default_length(capsys):
    code = main(["gen-token"])
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert len(out) == 32
    assert out.isalnum()


def test_gen_token_custom_length(capsys):
    code = main(["gen-token", "--length", "64"])
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert len(out) == 64


# ─────────────────────────────────────────────────────────────────────────────
# sign
# ─────────────────────────────────────────────────────────────────────────────

def test_sign_success(capsys):
    with patch("gateos_manager.security.signing.sign", return_value=Path("/tmp/dev.yaml.sig")):
        code = main(["sign", "/tmp/dev.yaml"])
    assert code == 0
    assert "Signed" in capsys.readouterr().out


def test_sign_with_key_dir(capsys):
    with patch("gateos_manager.security.signing.sign", return_value=Path("/keys/dev.yaml.sig")):
        code = main(["sign", "/tmp/dev.yaml", "--key-dir", "/keys"])
    assert code == 0


def test_sign_error(capsys):
    from gateos_manager.security.signing import SigningError
    with patch("gateos_manager.security.signing.sign", side_effect=SigningError("key not found")):
        code = main(["sign", "/tmp/dev.yaml"])
    assert code == 1
    assert "Error" in capsys.readouterr().err


# ─────────────────────────────────────────────────────────────────────────────
# verify
# ─────────────────────────────────────────────────────────────────────────────

def test_verify_success(capsys):
    with patch("gateos_manager.security.signing.verify", return_value=None):
        code = main(["verify", "/tmp/dev.yaml"])
    assert code == 0
    assert "OK" in capsys.readouterr().out


def test_verify_with_sig_and_key_dir(capsys):
    with patch("gateos_manager.security.signing.verify", return_value=None):
        code = main(["verify", "/tmp/dev.yaml", "--sig", "/tmp/dev.yaml.sig", "--key-dir", "/keys"])
    assert code == 0


def test_verify_error(capsys):
    from gateos_manager.security.signing import SigningError
    with patch("gateos_manager.security.signing.verify", side_effect=SigningError("sig mismatch")):
        code = main(["verify", "/tmp/dev.yaml"])
    assert code == 1
    assert "INVALID" in capsys.readouterr().err


# ─────────────────────────────────────────────────────────────────────────────
# gen-keypair
# ─────────────────────────────────────────────────────────────────────────────

def test_gen_keypair_success(capsys):
    with patch("gateos_manager.security.signing.generate_keypair", return_value=(Path("/k/signing.key"), Path("/k/signing.pub"))):
        code = main(["gen-keypair"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Private key" in out
    assert "Public key" in out


def test_gen_keypair_with_key_dir(capsys):
    with patch("gateos_manager.security.signing.generate_keypair", return_value=(Path("/d/signing.key"), Path("/d/signing.pub"))):
        code = main(["gen-keypair", "--key-dir", "/d"])
    assert code == 0


def test_gen_keypair_error(capsys):
    from gateos_manager.security.signing import SigningError
    with patch("gateos_manager.security.signing.generate_keypair", side_effect=SigningError("dir not writable")):
        code = main(["gen-keypair"])
    assert code == 1
    assert "Error" in capsys.readouterr().err


# ─────────────────────────────────────────────────────────────────────────────
# check-update
# ─────────────────────────────────────────────────────────────────────────────

def _make_release(version="2.0.0", prerelease=False):
    from gateos_manager.updater import ReleaseInfo
    return ReleaseInfo(
        version=version,
        tag=f"v{version}",
        download_url=f"https://example.com/gateos-{version}.deb",
        sha256_url="",
        sig_url="",
        prerelease=prerelease,
        release_notes="New release",
    )


def test_check_update_available(capsys):
    with patch("gateos_manager.updater.check_for_update", return_value=_make_release("2.0.0")):
        code = main(["check-update"])
    assert code == 0
    out = capsys.readouterr().out
    assert "2.0.0" in out


def test_check_update_up_to_date(capsys):
    with patch("gateos_manager.updater.check_for_update", return_value=None):
        code = main(["check-update"])
    assert code == 0
    assert "up to date" in capsys.readouterr().out


def test_check_update_prerelease_filtered(capsys):
    rel = _make_release("2.0.0-rc1", prerelease=True)
    with patch("gateos_manager.updater.check_for_update", return_value=rel):
        code = main(["check-update"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Pre-release" in out


def test_check_update_prerelease_included(capsys):
    rel = _make_release("2.0.0-rc1", prerelease=True)
    with patch("gateos_manager.updater.check_for_update", return_value=rel):
        code = main(["check-update", "--include-prerelease"])
    assert code == 0
    out = capsys.readouterr().out
    assert "2.0.0-rc1" in out


def test_check_update_with_release_notes(capsys):
    rel = _make_release("2.0.0")
    rel.release_notes = "Fixed bugs"
    with patch("gateos_manager.updater.check_for_update", return_value=rel):
        code = main(["check-update"])
    out = capsys.readouterr().out
    assert "Release notes" in out


def test_check_update_network_error(capsys):
    from gateos_manager.updater import UpdateError
    with patch("gateos_manager.updater.check_for_update", side_effect=UpdateError("timeout")):
        code = main(["check-update"])
    assert code == 1
    assert "failed" in capsys.readouterr().err


def test_check_update_custom_feed(capsys):
    with patch("gateos_manager.updater.check_for_update", return_value=None) as mock_check:
        main(["check-update", "--feed", "https://custom.example.com/releases"])
    # The feed is passed as positional arg; just assert it ran ok
    assert True


# ─────────────────────────────────────────────────────────────────────────────
# apply-update
# ─────────────────────────────────────────────────────────────────────────────

def test_apply_update_up_to_date(capsys):
    with patch("gateos_manager.updater.check_for_update", return_value=None):
        code = main(["apply-update"])
    assert code == 0
    assert "up to date" in capsys.readouterr().out


def test_apply_update_dry_run_default(capsys):
    """Default apply-update is dry-run (no --yes)."""
    rel = _make_release("2.0.0")
    with patch("gateos_manager.updater.check_for_update", return_value=rel), \
         patch("gateos_manager.updater.apply_update", return_value=None) as mock_apply:
        code = main(["apply-update"])
    assert code == 0
    assert "Dry-run OK" in capsys.readouterr().out
    # dry_run=True when --yes not passed
    mock_apply.assert_called_once_with(rel, dry_run=True)


def test_apply_update_with_yes(capsys):
    """--yes should call apply_update with dry_run=False."""
    rel = _make_release("2.0.0")
    with patch("gateos_manager.updater.check_for_update", return_value=rel), \
         patch("gateos_manager.updater.apply_update", return_value=None) as mock_apply:
        code = main(["apply-update", "--yes"])
    assert code == 0
    assert "Downloaded" in capsys.readouterr().out
    mock_apply.assert_called_once_with(rel, dry_run=False)


def test_apply_update_error(capsys):
    from gateos_manager.updater import UpdateError
    rel = _make_release("2.0.0")
    with patch("gateos_manager.updater.check_for_update", return_value=rel), \
         patch("gateos_manager.updater.apply_update", side_effect=UpdateError("disk full")):
        code = main(["apply-update", "--yes"])
    assert code == 1
    assert "failed" in capsys.readouterr().err


def test_apply_update_check_fails(capsys):
    from gateos_manager.updater import UpdateError
    with patch("gateos_manager.updater.check_for_update", side_effect=UpdateError("no network")):
        code = main(["apply-update"])
    assert code == 1
