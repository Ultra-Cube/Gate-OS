"""Phase 13.1 — API Security tests.

Covers:
 - POST /auth/rotate-token endpoint
 - OIDC stub (verify_oidc_token)
 - WebSocket bearer token auth (code 4401 when rejected)
 - Rate limit env-var window (already via rate_limit module, new param check)
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from gateos_manager.api.auth import (
    rotate_token,
    verify_token,
    verify_oidc_token,
    _oidc_enabled,
)
from gateos_manager.api.server import app


# ---------------------------------------------------------------------------
# rotate_token() unit tests
# ---------------------------------------------------------------------------

class TestRotateToken:
    def test_returns_64_hex_string_by_default(self, monkeypatch):
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        tok = rotate_token()
        assert isinstance(tok, str)
        assert len(tok) == 64
        assert all(c in "0123456789abcdef" for c in tok)

    def test_custom_token_accepted(self, monkeypatch):
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        tok = rotate_token(new_token="my-custom-token")
        assert tok == "my-custom-token"

    def test_updates_env_when_no_file(self, monkeypatch):
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        new_tok = rotate_token()
        assert os.getenv("GATEOS_API_TOKEN") == new_tok

    def test_writes_token_file_when_configured(self, tmp_path, monkeypatch):
        token_file = tmp_path / "token.txt"
        token_file.write_text("oldtoken\n", encoding="utf-8")
        monkeypatch.setenv("GATEOS_API_TOKEN_FILE", str(token_file))
        new_tok = rotate_token()
        assert token_file.read_text().strip() == new_tok

    def test_error_on_unwritable_file(self, tmp_path, monkeypatch):
        bad_path = tmp_path / "nonexistent_dir" / "token.txt"
        monkeypatch.setenv("GATEOS_API_TOKEN_FILE", str(bad_path))
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        with pytest.raises(RuntimeError, match="Failed to write token file"):
            rotate_token()

    def test_rotated_token_validates(self, monkeypatch):
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        new_tok = rotate_token()
        assert verify_token(new_tok) is True
        assert verify_token("wrong") is False


# ---------------------------------------------------------------------------
# POST /auth/rotate-token endpoint
# ---------------------------------------------------------------------------

class TestRotateTokenEndpoint:
    def test_rotate_endpoint_requires_auth(self, monkeypatch):
        monkeypatch.setenv("GATEOS_API_TOKEN", "secret")
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        client = TestClient(app)
        resp = client.post("/auth/rotate-token", headers={"x-token": "wrong"})
        assert resp.status_code == 401

    def test_rotate_endpoint_returns_new_token(self, monkeypatch):
        monkeypatch.setenv("GATEOS_API_TOKEN", "secret")
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        client = TestClient(app)
        resp = client.post("/auth/rotate-token", headers={"x-token": "secret"})
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body
        assert len(body["token"]) == 64
        assert body["message"] == "Token rotated successfully"

    def test_rotate_endpoint_no_auth_mode(self, monkeypatch):
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        client = TestClient(app)
        resp = client.post("/auth/rotate-token")
        assert resp.status_code == 200  # dev mode — no token configured


# ---------------------------------------------------------------------------
# OIDC stub
# ---------------------------------------------------------------------------

class TestOIDCStub:
    def test_oidc_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("GATEOS_OIDC_ISSUER", raising=False)
        assert _oidc_enabled() is False
        assert verify_oidc_token("x" * 40) is False

    def test_oidc_enabled_accepts_long_token(self, monkeypatch):
        monkeypatch.setenv("GATEOS_OIDC_ISSUER", "http://localhost:8080/realms/gateos")
        monkeypatch.delenv("GATEOS_OIDC_VERIFY_SIG", raising=False)
        assert _oidc_enabled() is True
        assert verify_oidc_token("x" * 20) is True

    def test_oidc_rejects_short_token(self, monkeypatch):
        monkeypatch.setenv("GATEOS_OIDC_ISSUER", "http://localhost:8080/realms/gateos")
        assert verify_oidc_token("short") is False

    def test_oidc_rejects_none(self, monkeypatch):
        monkeypatch.setenv("GATEOS_OIDC_ISSUER", "http://localhost:8080/realms/gateos")
        assert verify_oidc_token(None) is False

    def test_oidc_disabled_returns_false_regardless(self, monkeypatch):
        monkeypatch.delenv("GATEOS_OIDC_ISSUER", raising=False)
        assert verify_oidc_token("x" * 100) is False


# ---------------------------------------------------------------------------
# switch_environment uses OIDC bearer via Authorization header
# ---------------------------------------------------------------------------

class TestSwitchWithOIDCBearer:
    def test_switch_accepts_oidc_bearer_when_no_static_token(self, monkeypatch):
        """When OIDC enabled + no static token, bearer accepted even without x-token."""
        monkeypatch.setenv("GATEOS_OIDC_ISSUER", "http://localhost:8080")
        monkeypatch.delenv("GATEOS_OIDC_VERIFY_SIG", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        monkeypatch.delenv("GATEOS_API_RATE_LIMIT", raising=False)
        client = TestClient(app)
        # Environment doesn't exist → 404, but should not be 401
        resp = client.post(
            "/switch/nonexistent",
            headers={"Authorization": "Bearer " + "x" * 40},
        )
        assert resp.status_code == 404

    def test_switch_rejects_without_any_auth_when_token_configured(self, monkeypatch):
        monkeypatch.setenv("GATEOS_API_TOKEN", "tok123")
        monkeypatch.delenv("GATEOS_OIDC_ISSUER", raising=False)
        monkeypatch.delenv("GATEOS_API_RATE_LIMIT", raising=False)
        client = TestClient(app)
        resp = client.post("/switch/nonexistent")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# WebSocket auth
# ---------------------------------------------------------------------------

class TestWebSocketAuth:
    def test_ws_accepts_valid_token_as_query_param(self, monkeypatch):
        monkeypatch.setenv("GATEOS_API_TOKEN", "wstoken")
        monkeypatch.delenv("GATEOS_OIDC_ISSUER", raising=False)
        client = TestClient(app)
        with client.websocket_connect("/ws/status?token=wstoken") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "status"

    def test_ws_rejects_wrong_token(self, monkeypatch):
        monkeypatch.setenv("GATEOS_API_TOKEN", "wstoken")
        monkeypatch.delenv("GATEOS_OIDC_ISSUER", raising=False)
        client = TestClient(app)
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/status?token=wrong"):
                pass

    def test_ws_accepts_no_token_when_auth_disabled(self, monkeypatch):
        monkeypatch.delenv("GATEOS_API_TOKEN", raising=False)
        monkeypatch.delenv("GATEOS_API_TOKEN_FILE", raising=False)
        monkeypatch.delenv("GATEOS_OIDC_ISSUER", raising=False)
        client = TestClient(app)
        with client.websocket_connect("/ws/status") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "status"
