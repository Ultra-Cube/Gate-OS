"""Gate-OS switch button widget.

A compound widget that shows the current environment name and a
"Switch" button.  While a switch is in progress it replaces the
button label with a GTK ``Gtk.Spinner`` so the user sees immediate
feedback.

GObject signals emitted:
  switch-started(name: str)  — before the API call
  switch-done(name: str)     — after a successful switch
  switch-failed(name: str, error: str) — after a failed switch
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from gateos_manager.ui import require_gtk
from gateos_manager.logging.structured import error as log_error, info

require_gtk()

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, GObject, Gtk  # noqa: E402

if TYPE_CHECKING:
    from gateos_manager.ui.api_client import GateOSAPI


class SwitchButton(Gtk.Box):
    """Compound widget: current-env label + animated switch button."""

    __gtype_name__ = "GateOSSwitchButton"

    @GObject.Signal(arg_types=(str,))
    def switch_started(self, name: str) -> None:  # type: ignore[empty-body]
        """Emitted just before the API call is made."""
        ...

    @GObject.Signal(arg_types=(str,))
    def switch_done(self, name: str) -> None:  # type: ignore[empty-body]
        """Emitted when the environment switch succeeds."""
        ...

    @GObject.Signal(arg_types=(str, str))
    def switch_failed(self, name: str, error_msg: str) -> None:  # type: ignore[empty-body]
        """Emitted when the switch call fails."""
        ...

    def __init__(self, api: "GateOSAPI") -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._api = api
        self._target: str = ""
        self._busy = False

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        # ── Status label ──────────────────────────────────────────────────────
        self._status_label = Gtk.Label(label="No environment active")
        self._status_label.add_css_class("title-2")
        self._status_label.set_halign(Gtk.Align.CENTER)
        self.append(self._status_label)

        # ── Button stack: normal button ↔ spinner ─────────────────────────────
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._stack.set_transition_duration(150)
        self.append(self._stack)

        self._btn = Gtk.Button.new_with_label("Switch")
        self._btn.add_css_class("pill")
        self._btn.add_css_class("suggested-action")
        self._btn.set_halign(Gtk.Align.CENTER)
        self._btn.connect("clicked", self._on_switch_clicked)

        self._spinner_box = Gtk.Box(halign=Gtk.Align.CENTER)
        self._spinner = Gtk.Spinner()
        self._spinner.set_size_request(24, 24)
        self._spinner_box.append(self._spinner)

        self._stack.add_named(self._btn, "button")
        self._stack.add_named(self._spinner_box, "spinner")
        self._stack.set_visible_child_name("button")

        # ── Status badge (success / failure) ─────────────────────────────────
        self._badge = Gtk.Label(label="")
        self._badge.set_halign(Gtk.Align.CENTER)
        self._badge.set_visible(False)
        self.append(self._badge)

    # ── public helpers ────────────────────────────────────────────────────────

    def set_target_env(self, name: str) -> None:
        """Set the environment name that will be switched to on click."""
        self._target = name
        self._btn.set_label(f"Switch to {name.replace('-', ' ').title()}")
        self._badge.set_visible(False)

    def set_current_env(self, name: str) -> None:
        """Update the status label to show the currently active environment."""
        self._status_label.set_label(
            f"Active: {name.replace('-', ' ').title()}" if name else "No environment active"
        )

    # ── internals ─────────────────────────────────────────────────────────────

    def _on_switch_clicked(self, _btn: Gtk.Button) -> None:
        if self._busy or not self._target:
            return
        self._set_busy(True)
        self.emit("switch-started", self._target)
        info("ui.switch_button.clicked", target=self._target)
        # Run the API call off the main thread via GLib idle
        GLib.idle_add(self._do_switch)

    def _do_switch(self) -> bool:
        name = self._target
        try:
            self._api.switch_environment(name)
            GLib.idle_add(self._on_switch_success, name)
        except Exception as exc:  # noqa: BLE001
            GLib.idle_add(self._on_switch_error, name, str(exc))
        return GLib.SOURCE_REMOVE

    def _on_switch_success(self, name: str) -> bool:
        self._set_busy(False)
        self.set_current_env(name)
        self._show_badge(f"✓ Switched to {name.replace('-', ' ').title()}", success=True)
        self.emit("switch-done", name)
        info("ui.switch_button.done", target=name)
        return GLib.SOURCE_REMOVE

    def _on_switch_error(self, name: str, exc_str: str) -> bool:
        self._set_busy(False)
        self._show_badge(f"✗ Switch failed: {exc_str[:60]}", success=False)
        self.emit("switch-failed", name, exc_str)
        log_error("ui.switch_button.failed", target=name, error=exc_str)
        return GLib.SOURCE_REMOVE

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        if busy:
            self._spinner.start()
            self._stack.set_visible_child_name("spinner")
        else:
            self._spinner.stop()
            self._stack.set_visible_child_name("button")

    def _show_badge(self, text: str, *, success: bool) -> None:
        self._badge.set_label(text)
        self._badge.set_visible(True)
        if success:
            self._badge.add_css_class("success")
            self._badge.remove_css_class("error")
        else:
            self._badge.add_css_class("error")
            self._badge.remove_css_class("success")


GObject.type_register(SwitchButton)
