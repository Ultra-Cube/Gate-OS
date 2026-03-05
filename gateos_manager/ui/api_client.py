"""Gate-OS API client for UI components.

Thin synchronous HTTP wrapper around the Gate-OS Control API
(FastAPI, see gateos_manager/api/server.py).  Used by GTK widgets
to fetch environment list and trigger switches.

Keeps GTK4 and network logic fully separated so widgets stay testable.
"""
from __future__ import annotations

import os
from typing import Any

import urllib.request
import urllib.error
import json


class APIError(Exception):
    """Raised when the Control API returns an unexpected response."""


class GateOSAPI:
    """Minimal synchronous client for the Gate-OS Control API."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ) -> None:
        from gateos_manager.ui import API_URL

        self.base_url = (base_url or API_URL).rstrip("/")
        self._token = token or os.getenv("GATEOS_API_TOKEN", "")

    # ── public API ────────────────────────────────────────────────────────────

    def list_environments(self) -> list[dict[str, Any]]:
        """Return list of environment dicts from GET /environments."""
        return self._get("/environments")  # type: ignore[return-value]

    def switch_environment(self, name: str) -> dict[str, Any]:
        """Trigger POST /switch/{name} and return response dict."""
        return self._post(f"/switch/{name}", data={})  # type: ignore[return-value]

    def health(self) -> dict[str, Any]:
        """Return GET /health response dict."""
        return self._get("/health")  # type: ignore[return-value]

    # ── internals ─────────────────────────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _get(self, path: str) -> Any:
        url = self.base_url + path
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise APIError(f"HTTP {exc.code} on GET {path}") from exc
        except OSError as exc:
            raise APIError(f"Connection error on GET {path}: {exc}") from exc

    def _post(self, path: str, data: dict[str, Any]) -> Any:
        url = self.base_url + path
        payload = json.dumps(data).encode()
        headers = {**self._headers(), "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise APIError(f"HTTP {exc.code} on POST {path}") from exc
        except OSError as exc:
            raise APIError(f"Connection error on POST {path}: {exc}") from exc
