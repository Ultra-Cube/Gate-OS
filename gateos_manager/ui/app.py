"""Gate-OS GTK4/Adwaita main application window.

Entry point:  ``gateos-ui``  →  ``gateos_manager.ui.app:main``

Layout:
  ┌─────────────────────────────────────────┐
  │  Header Bar  (title + refresh button)   │
  ├─────────────────────────────────────────┤
  │  Scrollable pane                        │
  │    ├─ EnvListPanel  (environment list)  │
  │    └─ SwitchButton  (active switch)     │
  ├─────────────────────────────────────────┤
  │  StatusBar   (env / api / version)      │
  └─────────────────────────────────────────┘

Environment Variables:
  GATEOS_UI_NO_DISPLAY=1  — exit immediately (CI / test mode)
  GATEOS_API_URL          — Control API URL
  GATEOS_API_TOKEN        — Bearer token
"""
from __future__ import annotations

import os
import sys

from gateos_manager.ui import APP_ID, require_gtk
from gateos_manager.logging.structured import info

require_gtk()

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402

from gateos_manager.ui.api_client import GateOSAPI
from gateos_manager.ui.env_list import EnvListPanel
from gateos_manager.ui.status_bar import StatusBar
from gateos_manager.ui.switch_button import SwitchButton
from gateos_manager.ui.tray import AppIndicatorTray


class GateOSWindow(Adw.ApplicationWindow):
    """Main Gate-OS environment manager window."""

    def __init__(self, app: "GateOSApp") -> None:
        super().__init__(application=app)
        self.set_title("Gate-OS Manager")
        self.set_default_size(480, 640)
        self.set_resizable(True)

        self._api = GateOSAPI()

        # ── Outer layout ──────────────────────────────────────────────────────
        toolbar_view = Adw.ToolbarView()

        # Header bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)

        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh environments")
        refresh_btn.connect("clicked", self._on_refresh)
        header.pack_end(refresh_btn)

        toolbar_view.add_top_bar(header)

        # ── Scrollable content area ───────────────────────────────────────────
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)

        # Environment list
        self._env_list = EnvListPanel(self._api)
        self._env_list.connect("env-selected", self._on_env_selected)
        content_box.append(self._env_list)

        # Switch button panel
        self._switch_btn = SwitchButton(self._api)
        self._switch_btn.connect("switch-done", self._on_switch_done)
        content_box.append(self._switch_btn)

        scroll.set_child(content_box)
        toolbar_view.set_content(scroll)

        # Status bar
        self._status_bar = StatusBar(self._api)
        toolbar_view.add_bottom_bar(self._status_bar)

        self.set_content(toolbar_view)

        # Tray icon (optional)
        self._tray = AppIndicatorTray(self._api)
        self._tray.connect("env-selected", self._on_env_selected)

        # Initial data load
        GLib.idle_add(self._initial_load)

    # ── callbacks ─────────────────────────────────────────────────────────────

    def _initial_load(self) -> bool:
        self._env_list.refresh()
        self._status_bar.start_polling()
        return GLib.SOURCE_REMOVE

    def _on_refresh(self, _btn: Gtk.Button) -> None:
        self._env_list.refresh()
        info("ui.window.refresh")

    def _on_env_selected(self, _widget, name: str) -> None:
        self._switch_btn.set_target_env(name)
        info("ui.window.env_selected", name=name)

    def _on_switch_done(self, _widget, name: str) -> None:
        self._status_bar.set_active_env(name)
        self._tray.set_active_env(name)

    def do_close_request(self) -> bool:  # type: ignore[override]
        self._status_bar.stop_polling()
        return False  # allow default close behaviour


class GateOSApp(Adw.Application):
    """Gate-OS Adwaita application."""

    def __init__(self) -> None:
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self._window: GateOSWindow | None = None

    def do_activate(self) -> None:  # type: ignore[override]
        if self._window is None:
            self._window = GateOSWindow(self)
        self._window.present()
        info("ui.app.activated")

    def do_startup(self) -> None:  # type: ignore[override]
        Adw.Application.do_startup(self)
        info("ui.app.startup", app_id=APP_ID)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``gateos-ui`` command."""
    if os.getenv("GATEOS_UI_NO_DISPLAY") == "1":
        print("Gate-OS UI: display disabled (GATEOS_UI_NO_DISPLAY=1). Exiting.")
        return 0

    app = GateOSApp()
    return app.run(argv or sys.argv)
