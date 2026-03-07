"""Tests for gateos_manager.ui.dde_panel."""
from __future__ import annotations

from gateos_manager.ui.dde_panel import DDEPanelPlugin, DDE_AVAILABLE
from gateos_manager.ui.shell_adapter import NullShellAdapter, CallbackShellAdapter


def test_dde_available_is_bool():
    assert isinstance(DDE_AVAILABLE, bool)


def test_plugin_instantiates_without_dde():
    """DDEPanelPlugin must instantiate even without Deepin libraries."""
    plugin = DDEPanelPlugin()
    assert plugin is not None


def test_plugin_uses_null_adapter_by_default():
    plugin = DDEPanelPlugin()
    assert isinstance(plugin._adapter, NullShellAdapter)


def test_plugin_accepts_custom_adapter():
    events: list[tuple] = []
    adapter = CallbackShellAdapter(
        on_switch_cb=lambda n, ok, d: events.append((n, ok, d))
    )
    plugin = DDEPanelPlugin(adapter=adapter)
    plugin.notify_switch("gaming", True)
    assert events == [("gaming", True, "")]


def test_plugin_notify_switch_failure():
    events: list[tuple] = []
    adapter = CallbackShellAdapter(
        on_switch_cb=lambda n, ok, d: events.append((n, ok, d))
    )
    plugin = DDEPanelPlugin(adapter=adapter)
    plugin.notify_switch("security", False, "timeout")
    assert events[0] == ("security", False, "timeout")


def test_plugin_notify_switch_start():
    started: list[str] = []
    adapter = CallbackShellAdapter(
        on_switch_cb=lambda n, ok, d: None,
        on_start_cb=lambda n: started.append(n),
    )
    plugin = DDEPanelPlugin(adapter=adapter)
    plugin.notify_switch_start("design")
    assert started == ["design"]


def test_plugin_set_environments_updates_list():
    plugin = DDEPanelPlugin()
    plugin.set_environments(["dev", "gaming", "security"])
    assert plugin._envs == ["dev", "gaming", "security"]


def test_plugin_set_environments_fires_adapter_callback():
    listed: list[list] = []
    adapter = CallbackShellAdapter(
        on_switch_cb=lambda n, ok, d: None,
    )
    original = adapter.on_env_list_changed
    adapter.on_env_list_changed = lambda envs: listed.append(list(envs))  # type: ignore
    plugin = DDEPanelPlugin(adapter=adapter)
    plugin.set_environments(["media", "dev"])
    assert listed == [["media", "dev"]]


def test_plugin_constants():
    assert DDEPanelPlugin.PLUGIN_ID == "io.gateos.DDEPanel"
    assert DDEPanelPlugin.PLUGIN_VERSION == "1.0"
