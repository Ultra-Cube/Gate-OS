"""Gate-OS system tray icon using AyatanaAppIndicator3.

Provides quick-switch access from the system tray without opening
the full panel window.  Falls back gracefully when AyatanaAppIndicator3
is not available (e.g. GNOME without the extension).

GObject signals:  (see AppIndicatorTray class)
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable

from gateos_manager.ui import require_gtk
from gateos_manager.logging.structured import warn

require_gtk()

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")

from gi.repository import GObject  # noqa: E402

if TYPE_CHECKING:
    from gateos_manager.ui.api_client import GateOSAPI

# Optional AppIndicator support
_INDICATOR_AVAILABLE = False
try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3  # noqa: F401

    _INDICATOR_AVAILABLE = True
except Exception:  # noqa: BLE001
    pass


class AppIndicatorTray(GObject.Object):
    """System tray icon with environment quick-switch menu.

    Emits ``env-selected(name)`` when the user picks an environment
    from the tray menu.  If AyatanaAppIndicator3 is not available the
    object is created but :attr:`available` is ``False`` and no tray
    icon appears.
    """

    __gtype_name__ = "GateOSTrayIcon"

    @GObject.Signal(arg_types=(str,))
    def env_selected(self, name: str) -> None:  # type: ignore[empty-body]
        """Emitted when the user selects an environment from the tray."""
        ...

    def __init__(self, api: "GateOSAPI") -> None:
        super().__init__()
        self._api = api
        self._indicator = None
        self.available = _INDICATOR_AVAILABLE

        if not _INDICATOR_AVAILABLE:
            warn(
                "ui.tray.unavailable",
                detail="AyatanaAppIndicator3 not found; tray icon disabled",
            )
            return

        from gi.repository import AyatanaAppIndicator3 as AI  # type: ignore[import-not-found]

        self._indicator = AI.Indicator.new(
            "gate-os-manager",
            "appointment-new",  # fallback icon name
            AI.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_status(AI.IndicatorStatus.ACTIVE)
        self._build_menu()

    # ── public API ────────────────────────────────────────────────────────────

    def set_environments(self, envs: list[dict]) -> None:
        """Rebuild the tray menu with a fresh environment list."""
        if self._indicator is not None:
            self._build_menu(envs=envs)

    def set_active_env(self, name: str) -> None:
        """Update the tray tooltip / label to reflect the active env."""
        if self._indicator is not None:
            self._indicator.set_label(
                f"Gate-OS: {name.replace('-', ' ').title()}", "Gate-OS"
            )

    # ── internals ─────────────────────────────────────────────────────────────

    def _build_menu(self, envs: list[dict] | None = None) -> None:
        # GTK3 menu required by AppIndicator
        gi.require_version("Gtk", "3.0")  # noqa: F821 — only called when AI available
        from gi.repository import Gtk as Gtk3  # type: ignore[assignment]

        menu = Gtk3.Menu()

        if envs:
            for env in envs:
                name = env.get("metadata", {}).get("name") or env.get("name", "?")
                item = Gtk3.MenuItem.new_with_label(name.replace("-", " ").title())
                item.connect("activate", self._on_menu_activate, name)
                menu.append(item)
            menu.append(Gtk3.SeparatorMenuItem.new())

        quit_item = Gtk3.MenuItem.new_with_label("Quit Gate-OS Manager")
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)
        menu.show_all()

        self._indicator.set_menu(menu)  # type: ignore[union-attr]

    def _on_menu_activate(self, _item, name: str) -> None:
        self.emit("env-selected", name)

    def _on_quit(self, _item) -> None:
        import sys

        sys.exit(0)


GObject.type_register(AppIndicatorTray)
