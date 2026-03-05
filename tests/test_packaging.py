"""Tests for Gate-OS packaging utilities.

All file system operations are mocked so tests run without root access
or a real build environment.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gateos_manager.packaging import (
    PackagingError,
    build_deb,
    generate_postinstall_script,
    generate_preseed,
)


# ── build_deb ────────────────────────────────────────────────────────────────

class TestBuildDeb:
    """Tests for build_deb() in dry-run mode (no disk writes)."""

    def test_dry_run_does_not_raise(self, tmp_path, capsys):
        """build_deb with dry_run=True should print commands and return a Path."""
        src = tmp_path / "repo"
        src.mkdir()
        (src / "gateos_manager").mkdir()

        deb_path = build_deb(src, "0.2.0", tmp_path / "out", dry_run=True)
        assert deb_path.suffix == ".deb"
        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out

    def test_deb_filename_contains_version(self, tmp_path):
        src = tmp_path / "repo"
        src.mkdir()
        deb_path = build_deb(src, "1.2.3", tmp_path / "out", dry_run=True)
        assert "1.2.3" in deb_path.name

    def test_deb_filename_contains_arch(self, tmp_path):
        src = tmp_path / "repo"
        src.mkdir()
        deb_path = build_deb(src, "0.2.0", tmp_path / "out", dry_run=True)
        assert "amd64" in deb_path.name

    def test_packaging_error_on_dpkg_failure(self, tmp_path):
        """PackagingError raised when dpkg-deb returns non-zero (non-dry-run)."""
        src = tmp_path / "repo"
        (src / "gateos_manager").mkdir(parents=True)
        (src / "data" / "systemd").mkdir(parents=True)
        (src / "data" / "systemd" / "gateos-api.service").write_text("[Unit]\n")
        (src / "data" / "gate-os-manager.desktop").write_text("[Desktop Entry]\n")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="dpkg-deb: error")
            with pytest.raises(PackagingError, match="Command failed"):
                build_deb(src, "0.2.0", tmp_path / "out", dry_run=False)


# ── generate_preseed ─────────────────────────────────────────────────────────

class TestGeneratePreseed:
    def test_creates_file_with_preseed_content(self, tmp_path):
        out = tmp_path / "preseed.cfg"
        generate_preseed(out, dry_run=False)
        content = out.read_text()
        assert "debian-installer" in content
        assert "gate-os" in content

    def test_dry_run_does_not_create_file(self, tmp_path, capsys):
        out = tmp_path / "preseed.cfg"
        generate_preseed(out, dry_run=True)
        assert not out.exists()
        assert "DRY-RUN" in capsys.readouterr().out

    def test_preseed_contains_network_hostname(self, tmp_path):
        out = tmp_path / "preseed.cfg"
        generate_preseed(out, dry_run=False)
        assert "gate-os" in out.read_text()

    def test_preseed_enables_gateos_service(self, tmp_path):
        out = tmp_path / "preseed.cfg"
        generate_preseed(out, dry_run=False)
        assert "gateos-api.service" in out.read_text()


# ── generate_postinstall_script ───────────────────────────────────────────────

class TestGeneratePostinstallScript:
    def test_creates_executable_script(self, tmp_path):
        out = tmp_path / "postinstall.sh"
        generate_postinstall_script(out, dry_run=False)
        assert out.exists()
        # Check executable bit
        assert out.stat().st_mode & 0o111

    def test_script_contains_pip_install(self, tmp_path):
        out = tmp_path / "postinstall.sh"
        generate_postinstall_script(out, dry_run=False)
        content = out.read_text()
        assert "gateos-manager" in content

    def test_script_enables_service(self, tmp_path):
        out = tmp_path / "postinstall.sh"
        generate_postinstall_script(out, dry_run=False)
        assert "gateos-api.service" in out.read_text()

    def test_dry_run_does_not_create_file(self, tmp_path, capsys):
        out = tmp_path / "postinstall.sh"
        generate_postinstall_script(out, dry_run=True)
        assert not out.exists()
        assert "DRY-RUN" in capsys.readouterr().out

    def test_script_has_shebang(self, tmp_path):
        out = tmp_path / "postinstall.sh"
        generate_postinstall_script(out, dry_run=False)
        first_line = out.read_text().splitlines()[0]
        assert first_line.startswith("#!")

    def test_script_installs_python3(self, tmp_path):
        out = tmp_path / "postinstall.sh"
        generate_postinstall_script(out, dry_run=False)
        assert "python3" in out.read_text()
