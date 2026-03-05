"""Gate-OS GTK4/Adwaita UI Shell.

Provides the desktop panel for environment switching.
Requires PyGObject (gi) with GTK4 and Libadwaita.

Graceful degradation: importing this package WITHOUT GTK4 installed
raises :class:`GtkNotAvailableError` with a clear message instead of
a raw ImportError.

Environment Variables:
  GATEOS_UI_NO_DISPLAY=1  — skip display init (useful in CI / tests)
  GATEOS_API_URL          — Control API base URL (default: http://127.0.0.1:8088)
  GATEOS_API_TOKEN        — Bearer token for Control API
"""
from __future__ import annotations

__all__ = ["GtkNotAvailableError", "GTK_AVAILABLE", "APP_ID", "API_URL"]

import os

APP_ID = "io.gateos.Manager"
API_URL = os.getenv("GATEOS_API_URL", "http://127.0.0.1:8088")

GTK_AVAILABLE = False
_gtk_import_error: Exception | None = None

try:
    import gi  # noqa: F401

    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gtk  # noqa: F401

    GTK_AVAILABLE = True
except Exception as _exc:  # noqa: BLE001
    _gtk_import_error = _exc


class GtkNotAvailableError(RuntimeError):
    """Raised when GTK4/Adwaita is not installed on the system."""


def require_gtk() -> None:
    """Raise :class:`GtkNotAvailableError` if GTK4 is not available."""
    if not GTK_AVAILABLE:
        raise GtkNotAvailableError(
            "GTK4/Adwaita is not available on this system.\n"
            "Install with: sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1\n"
            f"Original error: {_gtk_import_error}"
        )
