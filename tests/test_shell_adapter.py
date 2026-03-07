"""Tests for gateos_manager.ui.shell_adapter."""
from __future__ import annotations

import pytest

from gateos_manager.ui.shell_adapter import (
    CallbackShellAdapter,
    NullShellAdapter,
    ShellAdapter,
)


# ── NullShellAdapter ───────────────────────────────────────────────────────────

def test_null_adapter_on_switch_does_not_raise():
    adapter = NullShellAdapter()
    adapter.on_switch("gaming", True)
    adapter.on_switch("gaming", False, "rollback triggered")


def test_null_adapter_on_switch_start_does_not_raise():
    adapter = NullShellAdapter()
    adapter.on_switch_start("security")


def test_null_adapter_on_env_list_changed_does_not_raise():
    adapter = NullShellAdapter()
    adapter.on_env_list_changed(["dev", "gaming", "design"])


# ── CallbackShellAdapter ───────────────────────────────────────────────────────

def test_callback_adapter_fires_on_switch():
    events: list[tuple] = []
    adapter = CallbackShellAdapter(on_switch_cb=lambda n, ok, d: events.append((n, ok, d)))
    adapter.on_switch("gaming", True, "")
    assert events == [("gaming", True, "")]


def test_callback_adapter_fires_on_switch_failure():
    events: list[tuple] = []
    adapter = CallbackShellAdapter(on_switch_cb=lambda n, ok, d: events.append((n, ok, d)))
    adapter.on_switch("security", False, "container failed to start")
    assert events[0][1] is False
    assert "container" in events[0][2]


def test_callback_adapter_fires_on_start():
    started: list[str] = []
    adapter = CallbackShellAdapter(
        on_switch_cb=lambda n, ok, d: None,
        on_start_cb=lambda n: started.append(n),
    )
    adapter.on_switch_start("media")
    assert started == ["media"]


def test_callback_adapter_no_start_cb_does_not_raise():
    adapter = CallbackShellAdapter(on_switch_cb=lambda n, ok, d: None)
    adapter.on_switch_start("dev")  # no on_start_cb provided — must not raise


def test_callback_adapter_env_list_changed_does_not_raise():
    adapter = CallbackShellAdapter(on_switch_cb=lambda n, ok, d: None)
    adapter.on_env_list_changed(["dev", "gaming"])


# ── ShellAdapter is abstract ───────────────────────────────────────────────────

def test_shell_adapter_is_abstract():
    with pytest.raises(TypeError):
        ShellAdapter()  # type: ignore[abstract]


def test_concrete_subclass_must_implement_on_switch():
    class Incomplete(ShellAdapter):
        pass

    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]


def test_concrete_subclass_without_optional_methods():
    """on_switch_start and on_env_list_changed have default no-op impls."""
    class Minimal(ShellAdapter):
        def on_switch(self, env_name, success, detail=""):
            pass

    m = Minimal()
    m.on_switch_start("dev")       # default no-op
    m.on_env_list_changed(["dev"]) # default no-op
