"""Gate-OS status bar widget.

Displays a compact bottom bar showing:
  - Current active environment name
  - API connection status (connected / disconnected)
  - Telemetry status (active / disabled)

Auto-refreshes every ``REFRESH_INTERVAL_MS`` milliseconds via GLib.timeout_add.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from gateos_manager.ui import require_gtk

require_gtk()

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import GLib, GObject, Gtk  # noqa: E402

if TYPE_CHECKING:
    from gateos_manager.ui.api_client import GateOSAPI

REFRESH_INTERVAL_MS = 5_000  # 5 seconds


class StatusBar(Gtk.ActionBar):
    """Bottom action bar showing live Gate-OS system status."""

    __gtype_name__ = "GateOSStatusBar"

    def __init__(self, api: "GateOSAPI") -> None:
        super().__init__()
        self._api = api
        self._timer_id: int | None = None

        # ── Left: active environment ──────────────────────────────────────────
        self._env_label = Gtk.Label(label="Environment: —")
        self._env_label.add_css_class("caption")
        self.pack_start(self._env_label)

        # ── Center: API status indicator ──────────────────────────────────────
        self._api_status = Gtk.Label(label="API: checking…")
        self._api_status.add_css_class("caption")
        self.set_center_widget(self._api_status)

        # ── Right: version ────────────────────────────────────────────────────
        from gateos_manager import __version__

        self._ver_label = Gtk.Label(label=f"Gate-OS v{__version__}")
        self._ver_label.add_css_class("caption")
        self._ver_label.add_css_class("dim-label")
        self.pack_end(self._ver_label)

    # ── public API ────────────────────────────────────────────────────────────

    def set_active_env(self, name: str) -> None:
        """Update the active environment label."""
        self._env_label.set_label(
            f"Active: {name.replace('-', ' ').title()}" if name else "Environment: —"
        )

    def start_polling(self) -> None:
        """Begin periodic refresh of API status."""
        self._refresh()
        if self._timer_id is None:
            self._timer_id = GLib.timeout_add(REFRESH_INTERVAL_MS, self._refresh)

    def stop_polling(self) -> None:
        """Stop the periodic refresh timer."""
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None

    # ── internals ─────────────────────────────────────────────────────────────

    def _refresh(self) -> bool:
        GLib.idle_add(self._check_api)
        return GLib.SOURCE_CONTINUE

    def _check_api(self) -> bool:
        try:
            self._api.health()
            self._api_status.set_label("API: ● connected")
            self._api_status.remove_css_class("error")
            self._api_status.add_css_class("success")
        except Exception:  # noqa: BLE001
            self._api_status.set_label("API: ✗ offline")
            self._api_status.remove_css_class("success")
            self._api_status.add_css_class("error")
        return GLib.SOURCE_REMOVE


GObject.type_register(StatusBar)
