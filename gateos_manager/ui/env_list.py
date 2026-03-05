"""Gate-OS environment list widget.

An ``Adw.PreferencesGroup`` that displays available environments
(fetched from the Control API) and emits an ``env-selected`` signal
when the user chooses one.

Usage::

    from gateos_manager.ui.env_list import EnvListPanel

    panel = EnvListPanel(api_client)
    panel.connect("env-selected", lambda w, name: print("selected", name))
    panel.refresh()
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from gateos_manager.ui import require_gtk
from gateos_manager.logging.structured import error as log_error, info

require_gtk()

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GObject, Gtk  # noqa: E402

if TYPE_CHECKING:
    from gateos_manager.ui.api_client import GateOSAPI

# Environment category → accent colour hint (informational only, Adwaita handles theming)
_CATEGORY_ICONS: dict[str, str] = {
    "gaming": "applications-games-symbolic",
    "dev": "applications-development-symbolic",
    "design": "applications-graphics-symbolic",
    "media": "applications-multimedia-symbolic",
    "security": "security-high-symbolic",
}
_DEFAULT_ICON = "applications-system-symbolic"


class EnvRow(Adw.ActionRow):
    """A single environment row in the list."""

    __gtype_name__ = "GateOSEnvRow"

    def __init__(self, env: dict[str, Any]) -> None:
        super().__init__()
        self._env = env
        name: str = env.get("metadata", {}).get("name") or env.get("name", "unknown")
        desc: str = (
            env.get("metadata", {}).get("description")
            or env.get("spec", {}).get("description")
            or ""
        )
        category: str = env.get("spec", {}).get("category", "")

        self.set_title(name.replace("-", " ").title())
        if desc:
            self.set_subtitle(desc[:80])

        # Leading icon
        icon = Gtk.Image.new_from_icon_name(
            _CATEGORY_ICONS.get(category, _DEFAULT_ICON)
        )
        icon.set_icon_size(Gtk.IconSize.LARGE)
        self.add_prefix(icon)

        # Trailing switch button
        btn = Gtk.Button.new_with_label("Switch")
        btn.add_css_class("suggested-action")
        btn.set_valign(Gtk.Align.CENTER)
        btn.connect("clicked", self._on_switch_clicked)
        self.add_suffix(btn)

        self.set_activatable_widget(btn)

    @GObject.Property(type=str, default="")
    def env_name(self) -> str:  # type: ignore[override]
        return (
            self._env.get("metadata", {}).get("name")
            or self._env.get("name", "unknown")
        )

    def _on_switch_clicked(self, _btn: Gtk.Button) -> None:
        self.emit("env-switch-requested", self.env_name)

    # Custom signal
    @GObject.Signal(arg_types=(str,))
    def env_switch_requested(self, name: str) -> None:  # type: ignore[empty-body]
        ...


GObject.type_register(EnvRow)


class EnvListPanel(Adw.PreferencesGroup):
    """Scrollable panel listing all available Gate-OS environments."""

    __gtype_name__ = "GateOSEnvListPanel"

    @GObject.Signal(arg_types=(str,))
    def env_selected(self, name: str) -> None:  # type: ignore[empty-body]
        """Emitted when an environment switch is requested."""
        ...

    def __init__(self, api: "GateOSAPI") -> None:
        super().__init__()
        self._api = api
        self.set_title("Available Environments")
        self.set_description("Select an environment to switch to.")
        self._rows: list[EnvRow] = []

    def refresh(self) -> None:
        """Fetch environments from the API and rebuild the list rows."""
        # Clear existing rows
        for row in self._rows:
            self.remove(row)
        self._rows.clear()

        try:
            envs: list[dict[str, Any]] = self._api.list_environments()
        except Exception as exc:  # noqa: BLE001
            log_error("ui.env_list.refresh.error", error=str(exc))
            self._add_error_row(str(exc))
            return

        if not envs:
            self._add_placeholder_row()
            return

        for env in envs:
            row = EnvRow(env)
            row.connect("env-switch-requested", self._on_row_switch)
            self.add(row)
            self._rows.append(row)

        info("ui.env_list.refreshed", count=len(envs))

    # ── internals ─────────────────────────────────────────────────────────────

    def _on_row_switch(self, _row: EnvRow, name: str) -> None:
        self.emit("env-selected", name)

    def _add_error_row(self, message: str) -> None:
        row = Adw.ActionRow()
        row.set_title("Could not load environments")
        row.set_subtitle(message[:120])
        row.add_css_class("error")
        self.add(row)
        self._rows.append(row)  # type: ignore[arg-type]

    def _add_placeholder_row(self) -> None:
        row = Adw.ActionRow()
        row.set_title("No environments found")
        row.set_subtitle("Add YAML manifests to your environments directory.")
        self.add(row)
        self._rows.append(row)  # type: ignore[arg-type]


GObject.type_register(EnvListPanel)
