"""Shell adapter interface for desktop environment integration.

Provides an abstract callback protocol so different desktop shells
(GTK4/Adwaita, DDE panel, headless) can react to Gate-OS environment
switch events without coupling to a specific toolkit.

Usage::

    from gateos_manager.ui.shell_adapter import ShellAdapter, NullShellAdapter

    class MyAdapter(ShellAdapter):
        def on_switch(self, env_name: str, success: bool, detail: str = "") -> None:
            # update taskbar widget, send notification, etc.
            ...

    # Register with the switch pipeline:
    adapter = MyAdapter()
    adapter.on_switch("gaming", True)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class ShellAdapter(ABC):
    """Abstract base for desktop-shell environment-switch callbacks."""

    @abstractmethod
    def on_switch(
        self,
        env_name: str,
        success: bool,
        detail: str = "",
    ) -> None:
        """Called after an environment switch attempt.

        Args:
            env_name: Name of the target environment.
            success:  True if the switch completed without error.
            detail:   Optional human-readable detail (error message or status).
        """

    def on_switch_start(self, env_name: str) -> None:
        """Called when a switch is about to begin. Optional override."""

    def on_env_list_changed(self, env_names: list[str]) -> None:
        """Called when the available environment list changes. Optional override."""


class NullShellAdapter(ShellAdapter):
    """No-op adapter — silently discards all events (useful in tests / headless)."""

    def on_switch(self, env_name: str, success: bool, detail: str = "") -> None:
        pass


class CallbackShellAdapter(ShellAdapter):
    """Adapter backed by plain callables — useful for lightweight integrations.

    Args:
        on_switch_cb:  Called with (env_name, success, detail).
        on_start_cb:   Optional; called with (env_name,) when switch starts.
    """

    def __init__(
        self,
        on_switch_cb: Callable[[str, bool, str], None],
        on_start_cb: Callable[[str], None] | None = None,
    ) -> None:
        self._on_switch_cb = on_switch_cb
        self._on_start_cb = on_start_cb

    def on_switch(self, env_name: str, success: bool, detail: str = "") -> None:
        self._on_switch_cb(env_name, success, detail)

    def on_switch_start(self, env_name: str) -> None:
        if self._on_start_cb is not None:
            self._on_start_cb(env_name)
