"""Tests for Phase 5 — Security Hardening.

Covers:
- AppArmor profile file existence and basic syntax
- Seccomp JSON profile schema validity
- Manifest signing module (sign / verify / generate_keypair) using a temp key dir
- CLI `gateos sign`, `gateos verify`, `gateos gen-keypair` commands
"""
from __future__ import annotations

import base64
import json
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
APPARMOR_DIR = REPO_ROOT / "profiles" / "apparmor"
SECCOMP_DIR = REPO_ROOT / "profiles" / "seccomp"


# ──────────────────────────────────────────────────────────────────────────
# AppArmor profile tests
# ──────────────────────────────────────────────────────────────────────────

EXPECTED_APPARMOR_PROFILES = [
    "gateos-env-dev",
    "gateos-env-gaming",
    "gateos-env-security",
    "gateos-env-design",
    "gateos-env-media",
]


@pytest.mark.parametrize("profile_name", EXPECTED_APPARMOR_PROFILES)
def test_apparmor_profile_exists(profile_name):
    path = APPARMOR_DIR / profile_name
    assert path.exists(), f"Missing AppArmor profile: {path}"
    assert path.stat().st_size > 0, f"Empty AppArmor profile: {path}"


@pytest.mark.parametrize("profile_name", EXPECTED_APPARMOR_PROFILES)
def test_apparmor_profile_has_profile_declaration(profile_name):
    content = (APPARMOR_DIR / profile_name).read_text()
    assert re.search(r"^profile\s+gateos-env-", content, re.MULTILINE), (
        f"{profile_name}: missing 'profile gateos-env-*' declaration"
    )


@pytest.mark.parametrize("profile_name", EXPECTED_APPARMOR_PROFILES)
def test_apparmor_profile_denies_sensitive_files(profile_name):
    content = (APPARMOR_DIR / profile_name).read_text()
    # Every profile must explicitly deny /etc/shadow
    assert "deny /etc/shadow" in content, (
        f"{profile_name}: missing 'deny /etc/shadow'"
    )


def test_apparmor_security_profile_denies_gpu():
    content = (APPARMOR_DIR / "gateos-env-security").read_text()
    assert "deny /dev/dri" in content, "Security profile should deny GPU access"
    assert "deny /dev/nvidia" in content, "Security profile should deny Nvidia GPU access"


def test_apparmor_gaming_profile_allows_gpu():
    content = (APPARMOR_DIR / "gateos-env-gaming").read_text()
    assert "/dev/dri/" in content, "Gaming profile should allow GPU /dev/dri/"
    # Must not globally deny dri
    assert "deny /dev/dri/**" not in content


def test_apparmor_security_profile_has_audit_denies():
    content = (APPARMOR_DIR / "gateos-env-security").read_text()
    assert re.search(r"audit deny capability", content), (
        "Security profile should have audit deny capability entries"
    )


# ──────────────────────────────────────────────────────────────────────────
# Seccomp JSON profile tests
# ──────────────────────────────────────────────────────────────────────────

EXPECTED_SECCOMP_PROFILES = [
    "gateos-default.json",
    "gateos-security.json",
]


@pytest.mark.parametrize("filename", EXPECTED_SECCOMP_PROFILES)
def test_seccomp_profile_exists_and_valid_json(filename):
    path = SECCOMP_DIR / filename
    assert path.exists(), f"Missing seccomp profile: {path}"
    data = json.loads(path.read_text())
    assert isinstance(data, dict), "Seccomp profile must be a JSON object"


@pytest.mark.parametrize("filename", EXPECTED_SECCOMP_PROFILES)
def test_seccomp_profile_has_required_keys(filename):
    data = json.loads((SECCOMP_DIR / filename).read_text())
    assert "defaultAction" in data, f"{filename}: missing 'defaultAction'"
    assert "syscalls" in data, f"{filename}: missing 'syscalls'"
    assert isinstance(data["syscalls"], list)


def test_seccomp_default_allows_common_syscalls():
    data = json.loads((SECCOMP_DIR / "gateos-default.json").read_text())
    allowed = {name for entry in data["syscalls"] for name in entry.get("names", [])
               if entry.get("action") == "SCMP_ACT_ALLOW"}
    for syscall in ("read", "write", "open", "close", "exit_group", "mmap", "brk"):
        assert syscall in allowed, f"Default profile missing common syscall: {syscall}"


def test_seccomp_security_profile_blocks_module_loading():
    data = json.loads((SECCOMP_DIR / "gateos-security.json").read_text())
    blocked = {name for entry in data["syscalls"] for name in entry.get("names", [])
               if entry.get("action") == "SCMP_ACT_ERRNO"}
    assert "init_module" in blocked, "Security profile must block init_module"
    assert "finit_module" in blocked, "Security profile must block finit_module"
    assert "kexec_load" in blocked, "Security profile must block kexec_load"


def test_seccomp_default_action_is_deny():
    for filename in EXPECTED_SECCOMP_PROFILES:
        data = json.loads((SECCOMP_DIR / filename).read_text())
        assert data["defaultAction"] == "SCMP_ACT_ERRNO", (
            f"{filename}: defaultAction should be SCMP_ACT_ERRNO (deny-by-default)"
        )


# ──────────────────────────────────────────────────────────────────────────
# Signing module tests
# ──────────────────────────────────────────────────────────────────────────

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: F401
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

pytestmark_crypto = pytest.mark.skipif(
    not CRYPTO_AVAILABLE, reason="cryptography package not installed"
)


@pytest.fixture()
def signing_env(tmp_path):
    """Fixture: manifest file + temp key dir with a generated keypair."""
    from gateos_manager.security.signing import generate_keypair

    manifest = tmp_path / "test-env.manifest.yaml"
    manifest.write_text("name: test\ncategory: dev\nversion: '1.0'\n")

    key_dir = tmp_path / "keys"
    generate_keypair(key_dir)
    return manifest, key_dir


@pytestmark_crypto
def test_sign_creates_sig_file(signing_env):
    from gateos_manager.security.signing import sign

    manifest, key_dir = signing_env
    sig_path = sign(manifest, key_dir=key_dir)
    assert sig_path.exists()
    # Signature file should decode as base64
    raw = base64.b64decode(sig_path.read_text().strip())
    assert len(raw) == 64  # Ed25519 signature is always 64 bytes


@pytestmark_crypto
def test_verify_valid_signature(signing_env):
    from gateos_manager.security.signing import sign, verify

    manifest, key_dir = signing_env
    sign(manifest, key_dir=key_dir)
    assert verify(manifest, key_dir=key_dir) is True


@pytestmark_crypto
def test_verify_detects_tampered_manifest(signing_env):
    from gateos_manager.security.signing import sign, verify, SigningError

    manifest, key_dir = signing_env
    sign(manifest, key_dir=key_dir)
    # Tamper with the manifest after signing
    manifest.write_text("name: tampered\ncategory: gaming\n")
    with pytest.raises(SigningError, match="verification failed"):
        verify(manifest, key_dir=key_dir)


@pytestmark_crypto
def test_verify_missing_sig_raises(signing_env):
    from gateos_manager.security.signing import verify, SigningError

    manifest, key_dir = signing_env
    with pytest.raises(SigningError, match="not found"):
        verify(manifest, key_dir=key_dir)


def test_signing_requires_crypto_package(tmp_path, monkeypatch):
    """sign() should raise SigningError with install hint when cryptography missing."""
    import gateos_manager.security.signing as signing_mod

    monkeypatch.setattr(signing_mod, "_CRYPTO_AVAILABLE", False)
    from gateos_manager.security.signing import SigningError

    manifest = tmp_path / "env.yaml"
    manifest.write_text("name: test\n")
    with pytest.raises(SigningError, match="cryptography"):
        signing_mod.sign(manifest, key_dir=tmp_path)


# ──────────────────────────────────────────────────────────────────────────
# CLI integration tests
# ──────────────────────────────────────────────────────────────────────────

def test_cli_gen_keypair_creates_key_files(tmp_path):
    from gateos_manager.cli import main
    if not CRYPTO_AVAILABLE:
        pytest.skip("cryptography not installed")

    rc = main(["gen-keypair", "--key-dir", str(tmp_path / "keys")])
    assert rc == 0
    assert (tmp_path / "keys" / "signing.key").exists()
    assert (tmp_path / "keys" / "signing.pub").exists()


def test_cli_sign_and_verify(tmp_path):
    from gateos_manager.cli import main
    if not CRYPTO_AVAILABLE:
        pytest.skip("cryptography not installed")

    key_dir = tmp_path / "keys"
    manifest = tmp_path / "env.yaml"
    manifest.write_text("name: test\ncategory: dev\nversion: '1.0'\n")

    main(["gen-keypair", "--key-dir", str(key_dir)])
    rc_sign = main(["sign", str(manifest), "--key-dir", str(key_dir)])
    assert rc_sign == 0

    rc_verify = main(["verify", str(manifest), "--key-dir", str(key_dir)])
    assert rc_verify == 0


def test_cli_verify_fails_on_bad_sig(tmp_path, capsys):
    from gateos_manager.cli import main
    if not CRYPTO_AVAILABLE:
        pytest.skip("cryptography not installed")

    key_dir = tmp_path / "keys"
    manifest = tmp_path / "env.yaml"
    manifest.write_text("name: test\ncategory: dev\nversion: '1.0'\n")

    main(["gen-keypair", "--key-dir", str(key_dir)])
    main(["sign", str(manifest), "--key-dir", str(key_dir)])

    # Tamper
    manifest.write_text("name: hacked\ncategory: gaming\n")
    rc = main(["verify", str(manifest), "--key-dir", str(key_dir)])
    assert rc == 1
