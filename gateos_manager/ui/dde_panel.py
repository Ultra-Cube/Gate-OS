"""DDE (Deepin Desktop Environment) panel plugin stub for Gate-OS.

Registers a Gate-OS environment-list widget that can be embedded in the
Deepin taskbar via the DDE plugin framework.

This module degrades gracefully when Deepin libraries are not installed —
it exports ``DDE_AVAILABLE`` so callers can check before instantiating.

Environment Variables:
  GATEOS_API_URL    — Gate-OS Control API base URL (default: http://127.0.0.1:8088)
  GATEOS_API_TOKEN  — Bearer token for API calls
"""
from __future__ import annotations

import os
from typing import Any

from gateos_manager.ui.shell_adapter import ShellAdapter, NullShellAdapter

DDE_AVAILABLE = False
_dde_import_error: Exception | None = None

try:
    # Deepin panel SDK — only present on Deepin / UOS systems
    import dde_plugin_manager as _dpm  # type: ignore[import]  # noqa: F401
    DDE_AVAILABLE = True
except Exception as _exc:  # noqa: BLE001
    _dde_import_error = _exc


class DDEPanelPlugin:
    """Gate-OS environment selector widget for Deepin panel.

    When DDE libraries are available this registers itself with the DDE
    plugin manager.  When they are absent it operates as a headless stub
    so Gate-OS core functions continue to work on non-Deepin systems.

    Args:
        adapter: :class:`~gateos_manager.ui.shell_adapter.ShellAdapter` that
                 receives switch events.  Defaults to :class:`NullShellAdapter`.
    """

    PLUGIN_ID = "io.gateos.DDEPanel"
    PLUGIN_VERSION = "1.0"

    def __init__(self, adapter: ShellAdapter | None = None) -> None:
        self._adapter = adapter or NullShellAdapter()
        self._api_url = os.getenv("GATEOS_API_URL", "http://127.0.0.1:8088")
        self._api_token = os.getenv("GATEOS_API_TOKEN", "")
        self._envs: list[str] = []

        if DDE_AVAILABLE:
            self._register_with_dde()

    # ── public API ────────────────────────────────────────────────────────────

    def set_environments(self, env_names: list[str]) -> None:
        """Update the displayed list of available environments.

        Calls :py:meth:`ShellAdapter.on_env_list_changed` so the adapter
        can refresh any associated UI widget.
        """
        self._envs = list(env_names)
        self._adapter.on_env_list_changed(self._envs)
        self._refresh_widget()

    def notify_switch(self, env_name: str, success: bool, detail: str = "") -> None:
        """Propagate a switch result to the panel adapter."""
        self._adapter.on_switch(env_name, success, detail)
        self._refresh_widget()

    def notify_switch_start(self, env_name: str) -> None:
        """Notify the panel that a switch is starting (show spinner etc.)."""
        self._adapter.on_switch_start(env_name)

    # ── internals ─────────────────────────────────────────────────────────────

    def _register_with_dde(self) -> None:  # pragma: no cover — DDE not in CI
        """Register plugin with DDE plugin manager."""
        try:
            import dde_plugin_manager as dpm  # type: ignore[import]
            dpm.register(
                plugin_id=self.PLUGIN_ID,
                version=self.PLUGIN_VERSION,
                on_activate=self._on_dde_activate,
            )
        except Exception:  # noqa: BLE001
            pass

    def _on_dde_activate(self, context: Any = None) -> None:  # pragma: no cover
        """Called by DDE when the panel loads the plugin."""

    def _refresh_widget(self) -> None:
        """Trigger a widget repaint if DDE is connected."""
        # No-op in stub; DDE-connected subclass would call panel.update()
