"""Minimal token auth for Control API.

Two modes:
 - Environment variable GATEOS_API_TOKEN
 - Token file path via GATEOS_API_TOKEN_FILE (first line used)

If neither is set, auth is disabled (development mode).
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=1)
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
    required = _load_token()
    if required is None:  # auth disabled
        return True
    return presented == required
