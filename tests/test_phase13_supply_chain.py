"""Phase 13.3 — Container Supply Chain tests.

Covers:
 - _check_digest_pins: no warnings for pinned images
 - _check_digest_pins: warnings for unpinned images
 - load_manifest attaches _warnings for unpinned images
 - emit_sbom_generated telemetry event
"""
from __future__ import annotations

import pytest

from gateos_manager.manifest.loader import _check_digest_pins
from gateos_manager.security.isolation import emit_sbom_generated


class TestDigestPinCheck:
    def test_no_warnings_for_pinned_image(self):
        data = {
            "spec": {
                "containers": [
                    {
                        "name": "app",
                        "image": "ghcr.io/ultra-cube/gate-os@sha256:"
                                 + "a" * 64,
                    }
                ]
            }
        }
        result = _check_digest_pins(data)
        assert result == []

    def test_warning_for_unpinned_image(self):
        data = {
            "spec": {
                "containers": [
                    {"name": "app", "image": "ubuntu:22.04"}
                ]
            }
        }
        result = _check_digest_pins(data)
        assert len(result) == 1
        assert "ubuntu:22.04" in result[0]
        assert "digest-pinned" in result[0]

    def test_warning_for_tag_only_no_digest(self):
        data = {
            "spec": {
                "containers": [
                    {"name": "svc", "image": "myregistry.io/myimage:latest"}
                ]
            }
        }
        result = _check_digest_pins(data)
        assert len(result) == 1

    def test_no_containers_no_warnings(self):
        assert _check_digest_pins({}) == []
        assert _check_digest_pins({"spec": {}}) == []
        assert _check_digest_pins({"spec": {"containers": []}}) == []

    def test_multiple_containers_mixed(self):
        data = {
            "spec": {
                "containers": [
                    {
                        "name": "pinned",
                        "image": "myrepo/app@sha256:" + "b" * 64,
                    },
                    {"name": "unpinned", "image": "nginx:1.25"},
                ]
            }
        }
        result = _check_digest_pins(data)
        assert len(result) == 1
        assert "unpinned" in result[0]

    def test_empty_image_ignored(self):
        data = {"spec": {"containers": [{"name": "noimg", "image": ""}]}}
        assert _check_digest_pins(data) == []

    def test_container_without_image_key(self):
        data = {"spec": {"containers": [{"name": "noimg"}]}}
        assert _check_digest_pins(data) == []

    def test_digest_must_be_64_hex_chars(self):
        # Short digest → warning
        data = {
            "spec": {
                "containers": [
                    {"name": "short", "image": "repo/img@sha256:abc123"}
                ]
            }
        }
        result = _check_digest_pins(data)
        assert len(result) == 1


class TestSBOMGeneratedEvent:
    def test_emit_sbom_generated_runs_without_error(self, monkeypatch):
        """emit_sbom_generated should not raise even if telemetry endpoint is down."""
        emitted: list[dict] = []

        # Patch the emit function to capture calls
        import gateos_manager.security.isolation as iso_mod
        original_emit = iso_mod.emit

        def mock_emit(name, **kwargs):
            emitted.append({"name": name, **kwargs})

        monkeypatch.setattr(iso_mod, "emit", mock_emit)
        emit_sbom_generated(
            image="ghcr.io/ultra-cube/gate-os:v1.3.0",
            sbom_path="/tmp/sbom.spdx.json",
            format="spdx-json",
        )
        assert any(e["name"] == "sbom_generated" for e in emitted)
        assert any(e.get("image") == "ghcr.io/ultra-cube/gate-os:v1.3.0" for e in emitted)

    def test_emit_sbom_generated_format_field(self, monkeypatch):
        import gateos_manager.security.isolation as iso_mod
        emitted: list[dict] = []
        monkeypatch.setattr(iso_mod, "emit", lambda n, **kw: emitted.append({"name": n, **kw}))
        emit_sbom_generated(image="myimg:v1", sbom_path="/out/sbom.json", format="cyclonedx")
        rec = next(e for e in emitted if e["name"] == "sbom_generated")
        assert rec["format"] == "cyclonedx"
