"""Phase 13.4 — Telemetry TLS + PII Redaction tests.

Covers:
 - redact_attrs: built-in PII fields are always redacted
 - redact_attrs: custom fields via GATEOS_OTLP_PII_REDACT
 - redact_attrs: non-PII fields pass through unchanged
 - OTLPExporter: tls_cert param stored as SSLContext
 - OTLPExporter: GATEOS_OTLP_TLS_CERT env var picked up
 - export_log applies PII redaction before sending
"""
from __future__ import annotations

import os
import ssl
import tempfile
import unittest.mock as mock

import pytest

from gateos_manager.telemetry.otlp import OTLPExporter, redact_attrs, _pii_fields


class TestRedactAttrs:
    def test_password_always_redacted(self):
        result = redact_attrs({"password": "supersecret"})
        assert result["password"] == "<redacted>"

    def test_token_always_redacted(self):
        result = redact_attrs({"token": "abc123"})
        assert result["token"] == "<redacted>"

    def test_secret_always_redacted(self):
        result = redact_attrs({"secret": "hunter2"})
        assert result["secret"] == "<redacted>"

    def test_api_key_always_redacted(self):
        result = redact_attrs({"api_key": "xyz"})
        assert result["api_key"] == "<redacted>"

    def test_non_pii_field_passes_through(self):
        result = redact_attrs({"env": "gaming", "duration_ms": 42})
        assert result["env"] == "gaming"
        assert result["duration_ms"] == 42

    def test_case_insensitive_field_matching(self):
        result = redact_attrs({"Password": "s3cr3t", "TOKEN": "tok"})
        assert result["Password"] == "<redacted>"
        assert result["TOKEN"] == "<redacted>"

    def test_empty_attrs_returns_empty(self):
        assert redact_attrs({}) == {}

    def test_custom_pii_field_via_env(self, monkeypatch):
        monkeypatch.setenv("GATEOS_OTLP_PII_REDACT", "ssn,dob")
        result = redact_attrs({"ssn": "123-45-6789", "dob": "1990-01-01", "name": "Alice"})
        assert result["ssn"] == "<redacted>"
        assert result["dob"] == "<redacted>"
        assert result["name"] == "Alice"

    def test_multiple_custom_fields_via_env(self, monkeypatch):
        monkeypatch.setenv("GATEOS_OTLP_PII_REDACT", "phone , email")
        result = redact_attrs({"phone": "555-0100", "email": "a@b.com", "ok": 1})
        assert result["phone"] == "<redacted>"
        assert result["email"] == "<redacted>"
        assert result["ok"] == 1


class TestOTLPExporterTLS:
    def test_no_tls_cert_ssl_ctx_is_none(self, monkeypatch):
        monkeypatch.delenv("GATEOS_OTLP_TLS_CERT", raising=False)
        exp = OTLPExporter(tls_cert=None)
        assert exp._ssl_ctx is None

    def test_tls_cert_param_creates_ssl_context(self, tmp_path):
        # Generate a self-signed cert for testing
        cert_file = tmp_path / "ca.pem"
        # We can't easily create a real cert in tests; use mock instead
        with mock.patch("ssl.SSLContext.load_verify_locations") as mock_load:
            ctx_mock = mock.MagicMock(spec=ssl.SSLContext)
            with mock.patch("ssl.create_default_context", return_value=ctx_mock):
                exp = OTLPExporter(tls_cert=str(cert_file))
            ctx_mock.load_verify_locations.assert_called_once_with(str(cert_file))

    def test_tls_cert_env_var_creates_ssl_context(self, tmp_path, monkeypatch):
        cert_file = tmp_path / "ca.pem"
        monkeypatch.setenv("GATEOS_OTLP_TLS_CERT", str(cert_file))
        ctx_mock = mock.MagicMock(spec=ssl.SSLContext)
        with mock.patch("ssl.create_default_context", return_value=ctx_mock):
            exp = OTLPExporter()
        ctx_mock.load_verify_locations.assert_called_once_with(str(cert_file))

    def test_ssl_ctx_passed_to_urlopen(self, monkeypatch, tmp_path):
        """Verify SSL context is forwarded to urllib.request.urlopen."""
        monkeypatch.delenv("GATEOS_OTLP_DISABLE", raising=False)
        cert_file = tmp_path / "ca.pem"
        ctx_mock = mock.MagicMock(spec=ssl.SSLContext)
        ctx_mock.load_verify_locations = mock.MagicMock()
        with mock.patch("ssl.create_default_context", return_value=ctx_mock):
            exp = OTLPExporter(tls_cert=str(cert_file))

        with mock.patch("urllib.request.urlopen") as mock_open:
            mock_resp = mock.MagicMock()
            mock_resp.__enter__ = lambda s: mock_resp
            mock_resp.__exit__ = mock.MagicMock(return_value=False)
            mock_resp.read.return_value = b""
            mock_open.return_value = mock_resp
            exp.export_log("test.event", {"x": 1})
        # The context kwarg should be the ssl ctx
        call_kwargs = mock_open.call_args
        assert call_kwargs is not None
        # context= should be the ssl ctx mock
        assert call_kwargs.kwargs.get("context") is ctx_mock or (
            len(call_kwargs.args) >= 2 and call_kwargs.args[1] is ctx_mock
        )


class TestExportLogPIIRedaction:
    def test_pii_field_is_redacted_in_post(self, monkeypatch):
        monkeypatch.delenv("GATEOS_OTLP_DISABLE", raising=False)
        monkeypatch.delenv("GATEOS_OTLP_TLS_CERT", raising=False)
        exp = OTLPExporter()
        posted_bodies: list[bytes] = []

        import urllib.request as ur
        original_urlopen = ur.urlopen

        class FakeResp:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self): return b""

        def fake_urlopen(req, timeout=None, context=None):
            posted_bodies.append(req.data)
            return FakeResp()

        monkeypatch.setattr(ur, "urlopen", fake_urlopen)

        exp.export_log("auth.login", {"password": "hunter2", "user": "alice"})
        assert posted_bodies
        import json
        payload = json.loads(posted_bodies[0])
        attrs = payload["resourceLogs"][0]["scopeLogs"][0]["logRecords"][0]["attributes"]
        attr_map = {a["key"]: a["value"] for a in attrs}
        assert attr_map["password"]["stringValue"] == "<redacted>"
        assert attr_map["user"]["stringValue"] == "alice"
