"""
gateos_manager.security.signing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ed25519 manifest signing and verification.

Keys live in $GATEOS_KEY_DIR (default: /etc/gateos/keys/).
  private key: signing.key   (PEM, never written to disk by this module)
  public key:  signing.pub   (PEM, distributed with images)

Signatures are stored next to manifests as  <manifest>.sig
(64-byte raw Ed25519 signature, base64-encoded).
"""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional cryptography backend
# ---------------------------------------------------------------------------
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature

    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CRYPTO_AVAILABLE = False

_DEFAULT_KEY_DIR = Path(os.getenv("GATEOS_KEY_DIR", "/etc/gateos/keys"))
_KEY_FILE = "signing.key"
_PUB_FILE = "signing.pub"


class SigningError(Exception):
    """Raised when signing or verification fails."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sign(manifest_path: str | Path, *, key_dir: Path | None = None) -> Path:
    """Sign *manifest_path* with the Ed25519 private key and write a .sig file.

    Returns the path of the generated signature file.
    Raises :exc:`SigningError` on any failure.
    """
    manifest_path = Path(manifest_path)
    key_dir = key_dir or _DEFAULT_KEY_DIR
    sig_path = manifest_path.with_suffix(manifest_path.suffix + ".sig")

    _require_crypto()

    private_key = _load_private_key(key_dir / _KEY_FILE)
    payload = _canonical_payload(manifest_path)
    raw_sig: bytes = private_key.sign(payload)
    sig_path.write_text(base64.b64encode(raw_sig).decode())
    return sig_path


def verify(manifest_path: str | Path, sig_path: str | Path | None = None,
           *, key_dir: Path | None = None) -> bool:
    """Verify the Ed25519 signature of *manifest_path*.

    *sig_path* defaults to ``<manifest>.sig`` next to the manifest.
    Returns ``True`` on success.
    Raises :exc:`SigningError` if the signature is invalid or missing.
    """
    manifest_path = Path(manifest_path)
    if sig_path is None:
        sig_path = manifest_path.with_suffix(manifest_path.suffix + ".sig")
    sig_path = Path(sig_path)

    _require_crypto()

    if not sig_path.exists():
        raise SigningError(f"Signature file not found: {sig_path}")

    public_key = _load_public_key((key_dir or _DEFAULT_KEY_DIR) / _PUB_FILE)
    payload = _canonical_payload(manifest_path)
    raw_sig = base64.b64decode(sig_path.read_text().strip())

    try:
        public_key.verify(raw_sig, payload)
    except InvalidSignature as exc:
        raise SigningError(f"Signature verification failed for {manifest_path}") from exc

    return True


def generate_keypair(key_dir: Path | None = None) -> tuple[Path, Path]:
    """Generate a new Ed25519 keypair and save PEM files to *key_dir*.

    Returns ``(private_key_path, public_key_path)``.
    **For development / key-rotation use only.**
    """
    key_dir = key_dir or _DEFAULT_KEY_DIR
    _require_crypto()

    key_dir.mkdir(parents=True, exist_ok=True)
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    priv_path = key_dir / _KEY_FILE
    pub_path = key_dir / _PUB_FILE

    priv_path.write_bytes(
        priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    priv_path.chmod(0o600)

    pub_path.write_bytes(
        pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return priv_path, pub_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_crypto() -> None:
    if not _CRYPTO_AVAILABLE:
        raise SigningError(
            "The 'cryptography' package is required for manifest signing. "
            "Install it with: pip install cryptography"
        )


def _canonical_payload(manifest_path: Path) -> bytes:
    """Return a stable SHA-256 hash of the manifest bytes as the payload."""
    data = manifest_path.read_bytes()
    digest = hashlib.sha256(data).digest()
    return digest


def _load_private_key(path: Path) -> "Ed25519PrivateKey":
    if not path.exists():
        raise SigningError(f"Private key not found: {path}")
    try:
        return serialization.load_pem_private_key(path.read_bytes(), password=None)
    except Exception as exc:
        raise SigningError(f"Failed to load private key: {exc}") from exc


def _load_public_key(path: Path) -> "Ed25519PublicKey":
    if not path.exists():
        raise SigningError(f"Public key not found: {path}")
    try:
        return serialization.load_pem_public_key(path.read_bytes())
    except Exception as exc:
        raise SigningError(f"Failed to load public key: {exc}") from exc
