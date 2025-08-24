"""Minimal token auth for Control API.

Two modes:
 - Environment variable GATEOS_API_TOKEN
 - Token file path via GATEOS_API_TOKEN_FILE (first line used)

If neither is set, auth is disabled (development mode).
"""
from __future__ import annotations

import os


def _load_token() -> str | None:
    file_path = os.getenv("GATEOS_API_TOKEN_FILE")
    if file_path and os.path.exists(file_path):  # pragma: no cover - simple IO
        try:
            with open(file_path, encoding="utf-8") as f:
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
