"""Simple in-memory token bucket style rate limiter (per process).

Configured via environment variables:
  GATEOS_API_RATE_LIMIT = <int requests> (per window)
  GATEOS_API_RATE_WINDOW = <seconds window length> (default 60)

If GATEOS_API_RATE_LIMIT not set, rate limiting is disabled.
Not production grade (no distributed coordination, no eviction).
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class _Bucket:
    count: int
    reset_at: float


_buckets: Dict[str, _Bucket] = {}


def _config() -> tuple[int | None, int]:  # pragma: no cover - trivial
    limit_env = os.getenv("GATEOS_API_RATE_LIMIT")
    limit = int(limit_env) if limit_env and limit_env.isdigit() else None
    window = int(os.getenv("GATEOS_API_RATE_WINDOW") or 60)
    return limit, window


def consume(key: str) -> tuple[bool, int | None, int | None, float | None]:
    """Consume one request from bucket.

    Returns (allowed, limit, remaining, reset_at_epoch)
    If limit is None, unlimited and remaining None.
    """
    limit, window = _config()
    if limit is None:
        return True, None, None, None
    now = time.time()
    bucket = _buckets.get(key)
    if not bucket or now >= bucket.reset_at:
        _buckets[key] = _Bucket(count=1, reset_at=now + window)
        remaining = limit - 1
        return True, limit, remaining, _buckets[key].reset_at
    if bucket.count < limit:
        bucket.count += 1
        remaining = limit - bucket.count
        return True, limit, remaining, bucket.reset_at
    return False, limit, 0, bucket.reset_at
