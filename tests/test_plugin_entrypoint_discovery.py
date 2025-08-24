import importlib.metadata
import os

from gateos_manager.plugins.registry import discover_entrypoint_plugins


def test_discover_entrypoint_plugins_empty(monkeypatch):
    # Patch importlib.metadata.entry_points to return empty for our group
    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: {"gateos.plugins": []})
    plugins = discover_entrypoint_plugins(group="gateos.plugins")
    assert plugins == []

def test_discover_entrypoint_plugins_found(monkeypatch):
    class DummyEP:
        def load(self):
            return lambda: "plugin-loaded"
    class DummyEPs:
        def select(self, group=None):
            if group == "gateos.plugins":
                return [DummyEP()]
            return []
    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: DummyEPs())
    plugins = discover_entrypoint_plugins(group="gateos.plugins")
    assert len(plugins) == 1
    assert plugins[0]() == "plugin-loaded"

def test_discover_entrypoint_plugins_disabled(monkeypatch):
    os.environ["GATEOS_DISABLE_ENTRYPOINT_PLUGINS"] = "1"
    plugins = discover_entrypoint_plugins(group="gateos.plugins")
    assert plugins == []
    del os.environ["GATEOS_DISABLE_ENTRYPOINT_PLUGINS"]
