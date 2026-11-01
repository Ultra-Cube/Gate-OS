"""Phase 13.2 — Plugin Sandbox tests.

Covers:
 - _allow_unsigned() flag
 - _verify_plugin_signature() behaviour
 - discover_entrypoint_plugins with GATEOS_ALLOW_UNSIGNED_PLUGINS
 - GATEOS_DISABLE_ENTRYPOINT_PLUGINS still works
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from gateos_manager.plugins.registry import (
    _allow_unsigned,
    _verify_plugin_signature,
    discover_entrypoint_plugins,
)


class TestAllowUnsigned:
    def test_default_is_false(self, monkeypatch):
        monkeypatch.delenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", raising=False)
        assert _allow_unsigned() is False

    def test_true_string(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "true")
        assert _allow_unsigned() is True

    def test_1_string(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "1")
        assert _allow_unsigned() is True

    def test_yes_string(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "yes")
        assert _allow_unsigned() is True

    def test_false_string(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "false")
        assert _allow_unsigned() is False


class TestVerifyPluginSignature:
    def _make_ep(self, dist_name: str = "my-plugin"):
        ep = MagicMock()
        ep.value = f"{dist_name}.module:entry"
        ep.name = dist_name
        return ep

    def test_returns_false_when_no_dist_and_unsigned_disallowed(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "false")
        ep = self._make_ep("nonexistent-dist-xyz-999")
        # metadata.distribution will raise PackageNotFoundError → fallback to _allow_unsigned
        result = _verify_plugin_signature(ep)
        assert result is False

    def test_returns_true_when_unsigned_allowed_and_no_dist(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "true")
        ep = self._make_ep("nonexistent-dist-xyz-999")
        result = _verify_plugin_signature(ep)
        assert result is True

    def test_returns_true_when_dist_has_sig_file(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "false")
        ep = self._make_ep("signed-plugin")
        mock_dist = MagicMock()
        mock_dist.files = [MagicMock(__str__=lambda s: "RECORD.sig")]
        with patch("gateos_manager.plugins.registry.metadata.distribution",
                   return_value=mock_dist):
            result = _verify_plugin_signature(ep)
        assert result is True

    def test_returns_false_when_dist_has_no_sig_file_and_disallowed(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "false")
        ep = self._make_ep("unsigned-plugin")
        mock_dist = MagicMock()
        mock_dist.files = [MagicMock(__str__=lambda s: "RECORD")]
        with patch("gateos_manager.plugins.registry.metadata.distribution",
                   return_value=mock_dist):
            result = _verify_plugin_signature(ep)
        assert result is False

    def test_secure_mode_rejects_signature_without_verification_artifacts(self, monkeypatch):
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "false")
        monkeypatch.setenv("GATEOS_REQUIRE_PLUGIN_SIGNATURES", "1")
        ep = self._make_ep("signed-plugin")
        mock_dist = MagicMock()
        mock_dist.files = [MagicMock(__str__=lambda s: "RECORD.sig")]
        with patch("gateos_manager.plugins.registry.metadata.distribution", return_value=mock_dist):
            assert _verify_plugin_signature(ep) is False


class TestDiscoverWithSecurityFlags:
    def test_isolate_mode_does_not_load_plugin_in_process(self, monkeypatch):
        monkeypatch.delenv("GATEOS_DISABLE_ENTRYPOINT_PLUGINS", raising=False)
        monkeypatch.setenv("GATEOS_PLUGIN_ISOLATE", "1")
        monkeypatch.setenv("GATEOS_ALLOW_UNSIGNED_PLUGINS", "true")
        ep = MagicMock()
        ep.name = "isolated-plugin"
        ep.value = "isolated_plugin:entry"
        mock_eps = MagicMock()
        mock_eps.select.return_value = [ep]
        with patch("gateos_manager.plugins.registry.metadata.entry_points", return_value=mock_eps), \
             patch("gateos_manager.plugins.registry._load_plugin_isolated", return_value=True) as probe:
            assert discover_entrypoint_plugins() == []
        probe.assert_called_once_with(ep)
        ep.load.assert_not_called()

    def test_disable_flag_returns_empty(self, monkeypatch):
        monkeypatch.setenv("GATEOS_DISABLE_ENTRYPOINT_PLUGINS", "1")
        result = discover_entrypoint_plugins()
        assert result == []

    def test_no_entrypoints_returns_empty(self, monkeypatch):
        monkeypatch.delenv("GATEOS_DISABLE_ENTRYPOINT_PLUGINS", raising=False)
        # entry_points().select() returns empty iterable → no plugins
        mock_eps = MagicMock()
        mock_eps.select.return_value = []
        with patch("gateos_manager.plugins.registry.metadata.entry_points",
                   return_value=mock_eps):
            result = discover_entrypoint_plugins()
        assert result == []
