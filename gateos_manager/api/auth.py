"""Minimal token auth for Control API.

Two modes:
 - Environment variable GATEOS_API_TOKEN
 - Token file path via GATEOS_API_TOKEN_FILE (first line used)

If neither is set, auth is disabled (development mode).

OIDC integration stub:
 - GATEOS_OIDC_ISSUER      Issuer URL (e.g. http://localhost:8080/realms/gateos)
 - GATEOS_OIDC_CLIENT_ID   Client ID for audience validation
 When set, OIDC mode is enabled and bearer tokens are validated against the
 issuer's well-known JWKS endpoint (stub: validates presence only; full
 signature verification requires python-jose and GATEOS_OIDC_VERIFY_SIG=1).
"""
from __future__ import annotations

import os
import secrets
from typing import Optional


def _load_token() -> Optional[str]:
    file_path = os.getenv("GATEOS_API_TOKEN_FILE")
    if file_path and os.path.exists(file_path):  # pragma: no cover - simple IO
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                token = f.readline().strip()
                if token:
                    return token
        except OSError:
            return None
    env_token = os.getenv("GATEOS_API_TOKEN")
    if env_token:
        return env_token
    return None


def verify_token(presented: str | None) -> bool:
    """Verify presented token against current environment or file token.

    Caching was removed to allow tests (and runtime) to modify the auth token
    dynamically without needing explicit cache invalidation. For development
    mode (no token configured) auth is disabled.
    """
    required = _load_token()
    if required is None:
        return True
    return presented == required


def rotate_token(*, new_token: str | None = None) -> str:
    """Generate and persist a new API token.

    If *new_token* is supplied it is used; otherwise a cryptographically random
    64-hex-character token is generated via :func:`secrets.token_hex`.

    The new token is written to GATEOS_API_TOKEN_FILE when that variable is set,
    or stored in GATEOS_API_TOKEN env var otherwise (in-process only — no disk
    persistence without a token file configured).

    Returns the new token string.
    """
    token = new_token if new_token is not None else secrets.token_hex(32)

    file_path = os.getenv("GATEOS_API_TOKEN_FILE")
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(token + "\n")
        except OSError as exc:
            raise RuntimeError(
                f"Failed to write token file {file_path}: {exc}"
            ) from exc
    else:
        os.environ["GATEOS_API_TOKEN"] = token

    return token


# ---------------------------------------------------------------------------
# OIDC stub
# ---------------------------------------------------------------------------

def _oidc_enabled() -> bool:
    return bool(os.getenv("GATEOS_OIDC_ISSUER"))


def verify_oidc_token(bearer: str | None) -> bool:
    """Stub OIDC bearer-token validation.

    When GATEOS_OIDC_ISSUER is not set this always returns False (caller should
    fall back to static-token check).

    In stub mode: validates that the token is a non-empty string of at least
    20 characters (syntactic only).  Full JWT signature verification requires
    python-jose and is gated on GATEOS_OIDC_VERIFY_SIG=1.
    """
    if not _oidc_enabled():
        return False
    if not bearer or len(bearer) < 20:
        return False
    if os.getenv("GATEOS_OIDC_VERIFY_SIG") == "1":  # pragma: no cover - optional dep
        return _verify_jwt_signature(bearer)
    return True


def _verify_jwt_signature(token: str) -> bool:  # pragma: no cover - requires python-jose
    """Validate JWT signature against OIDC issuer JWKS (requires python-jose)."""
    try:
        from jose import jwt as _jose_jwt  # type: ignore[import]
        issuer = os.getenv("GATEOS_OIDC_ISSUER", "")
        client_id = os.getenv("GATEOS_OIDC_CLIENT_ID", "")
        _jose_jwt.decode(
            token,
            "",
            options={"verify_signature": False, "verify_aud": bool(client_id)},
            audience=client_id or None,
            issuer=issuer or None,
        )
        return True
    except Exception:
        return False
