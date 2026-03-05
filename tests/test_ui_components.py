"""Tests for the Gate-OS UI components.

All GTK4/gi bindings are mocked so these tests can run in a headless
CI environment without GTK4 installed.  We test:

  - GtkNotAvailableError is raised appropriately
  - GateOSAPI client correctly builds URLs and passes tokens
  - GateOSAPI error handling on HTTP errors and connection failures
  - StatusBar / SwitchButton / EnvListPanel logic (mocked GTK)
  - AppIndicatorTray graceful degradation
  - main() respects GATEOS_UI_NO_DISPLAY
"""
from __future__ import annotations

import json
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers: build a minimal gi mock so we can import UI modules without GTK
# ---------------------------------------------------------------------------

def _make_gi_mock() -> types.ModuleType:
    """Return a minimal fake ``gi`` module tree."""
    gi = types.ModuleType("gi")
    repository = types.ModuleType("gi.repository")
    gi.repository = repository  # type: ignore[attr-defined]
    gi.require_version = MagicMock()

    # Minimal GObject mock
    gobject_mod = types.ModuleType("gi.repository.GObject")
    base = MagicMock()

    class FakeGObjectBase:
        def __init_subclass__(cls, **kw): pass
        def connect(self, *a, **kw): return 0
        def emit(self, *a, **kw): pass

    gobject_mod.Object = FakeGObjectBase
    gobject_mod.Property = lambda **kw: (lambda f: f)
    gobject_mod.Signal = lambda **kw: (lambda f: f)
    gobject_mod.type_register = MagicMock()

    # Minimal Gtk mock
    gtk_mod = types.ModuleType("gi.repository.Gtk")

    class Widget(FakeGObjectBase):
        def set_margin_top(self, v): pass
        def set_margin_bottom(self, v): pass
        def set_margin_start(self, v): pass
        def set_margin_end(self, v): pass
        def add_css_class(self, c): pass
        def remove_css_class(self, c): pass
        def set_visible(self, v): pass
        def set_halign(self, v): pass
        def set_valign(self, v): pass
        def set_vexpand(self, v): pass
        def append(self, w): pass
        def set_child(self, w): pass
        def set_tooltip_text(self, t): pass

    class Box(Widget):
        def __init__(self, **kw): pass

    class Label(Widget):
        def __init__(self, label=""): self._label = label
        def set_label(self, l): self._label = l
        def get_label(self): return self._label

    class Button(Widget):
        @classmethod
        def new_with_label(cls, l):
            b = cls(); b._label = l; return b
        @classmethod
        def new_from_icon_name(cls, n):
            return cls()
        def set_label(self, l): pass
        def connect(self, sig, cb, *a):
            if sig == "clicked": self._clicked_cb = cb

    class Spinner(Widget):
        def start(self): pass
        def stop(self): pass
        def set_size_request(self, w, h): pass

    class Stack(Widget):
        def add_named(self, w, n): pass
        def set_visible_child_name(self, n): pass
        def set_transition_type(self, t): pass
        def set_transition_duration(self, d): pass

    class ScrolledWindow(Widget):
        def set_policy(self, h, v): pass

    class Image(Widget):
        @classmethod
        def new_from_icon_name(cls, n):
            return cls()
        def set_icon_size(self, s): pass

    class ActionBar(Widget):
        def pack_start(self, w): pass
        def pack_end(self, w): pass
        def set_center_widget(self, w): pass

    class Menu(Widget):
        def __init__(self): self._items = []
        def append(self, item): self._items.append(item)
        def show_all(self): pass

    class MenuItem(Widget):
        def __init__(self): self._label = ""
        @classmethod
        def new_with_label(cls, l):
            m = cls(); m._label = l; return m
        def connect(self, sig, cb, *a): pass

    class SeparatorMenuItem(Widget):
        @classmethod
        def new(cls): return cls()

    gtk_mod.Box = Box
    gtk_mod.Label = Label
    gtk_mod.Button = Button
    gtk_mod.Spinner = Spinner
    gtk_mod.Stack = Stack
    gtk_mod.ScrolledWindow = ScrolledWindow
    gtk_mod.Image = Image
    gtk_mod.ActionBar = ActionBar
    gtk_mod.Menu = Menu
    gtk_mod.MenuItem = MenuItem
    gtk_mod.SeparatorMenuItem = SeparatorMenuItem
    gtk_mod.Align = MagicMock()
    gtk_mod.Align.CENTER = 3
    gtk_mod.Align.START = 1
    gtk_mod.Orientation = MagicMock()
    gtk_mod.Orientation.VERTICAL = 1
    gtk_mod.PolicyType = MagicMock()
    gtk_mod.PolicyType.NEVER = 0
    gtk_mod.PolicyType.AUTOMATIC = 1
    gtk_mod.IconSize = MagicMock()
    gtk_mod.IconSize.LARGE = 2
    gtk_mod.StackTransitionType = MagicMock()
    gtk_mod.StackTransitionType.CROSSFADE = 1

    # Adw mock
    adw_mod = types.ModuleType("gi.repository.Adw")

    class Application(FakeGObjectBase):
        def __init__(self, **kw): pass
        def run(self, argv=None): return 0
        def do_startup(self): pass

    class ApplicationWindow(Widget):
        def __init__(self, **kw): pass
        def set_title(self, t): pass
        def set_default_size(self, w, h): pass
        def set_resizable(self, v): pass
        def set_content(self, w): pass
        def present(self): pass

    class HeaderBar(Widget):
        def set_show_end_title_buttons(self, v): pass
        def pack_end(self, w): pass
        def pack_start(self, w): pass

    class ActionRow(Widget):
        def __init__(self, **kw): pass
        def set_title(self, t): self._title = t
        def set_subtitle(self, s): pass
        def add_prefix(self, w): pass
        def add_suffix(self, w): pass
        def set_activatable_widget(self, w): pass
        def remove(self, w): pass

    class PreferencesGroup(Widget):
        def __init__(self, **kw): pass
        def set_title(self, t): pass
        def set_description(self, d): pass
        def add(self, w): pass
        def remove(self, w): pass

    class ToolbarView(Widget):
        def add_top_bar(self, w): pass
        def add_bottom_bar(self, w): pass
        def set_content(self, w): pass

    adw_mod.Application = Application
    adw_mod.ApplicationWindow = ApplicationWindow
    adw_mod.HeaderBar = HeaderBar
    adw_mod.ActionRow = ActionRow
    adw_mod.PreferencesGroup = PreferencesGroup
    adw_mod.ToolbarView = ToolbarView

    # GLib mock
    glib_mod = types.ModuleType("gi.repository.GLib")
    glib_mod.idle_add = lambda f, *a: f(*a)
    glib_mod.timeout_add = lambda ms, f: 42
    glib_mod.source_remove = MagicMock()
    glib_mod.SOURCE_REMOVE = False
    glib_mod.SOURCE_CONTINUE = True

    # Gio mock
    gio_mod = types.ModuleType("gi.repository.Gio")
    gio_mod.ApplicationFlags = MagicMock()
    gio_mod.ApplicationFlags.DEFAULT_FLAGS = 0

    # Wire up
    repository.GObject = gobject_mod
    repository.Gtk = gtk_mod
    repository.Adw = adw_mod
    repository.GLib = glib_mod
    repository.Gio = gio_mod

    gi.repository.GObject = gobject_mod
    gi.repository.Gtk = gtk_mod
    gi.repository.Adw = adw_mod
    gi.repository.GLib = glib_mod
    gi.repository.Gio = gio_mod

    return gi


# Install global gi mock BEFORE importing any UI modules
_gi_mock = _make_gi_mock()
sys.modules["gi"] = _gi_mock
sys.modules["gi.repository"] = _gi_mock.repository
sys.modules["gi.repository.GObject"] = _gi_mock.repository.GObject
sys.modules["gi.repository.Gtk"] = _gi_mock.repository.Gtk
sys.modules["gi.repository.Adw"] = _gi_mock.repository.Adw
sys.modules["gi.repository.GLib"] = _gi_mock.repository.GLib
sys.modules["gi.repository.Gio"] = _gi_mock.repository.Gio

# ---------------------------------------------------------------------------
# Now we can safely import UI modules
# ---------------------------------------------------------------------------

import importlib
import gateos_manager.ui as ui_pkg  # reload not needed – first import

# Force GTK_AVAILABLE so require_gtk() doesn't raise
ui_pkg.GTK_AVAILABLE = True

from gateos_manager.ui.api_client import APIError, GateOSAPI  # noqa: E402
from gateos_manager.ui.env_list import EnvListPanel  # noqa: E402
from gateos_manager.ui.status_bar import StatusBar  # noqa: E402
from gateos_manager.ui.switch_button import SwitchButton  # noqa: E402
from gateos_manager.ui.tray import AppIndicatorTray  # noqa: E402
from gateos_manager.ui.app import GateOSApp, GateOSWindow  # noqa: E402


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGtkNotAvailableError(unittest.TestCase):
    def test_error_class_is_runtime_error(self):
        from gateos_manager.ui import GtkNotAvailableError
        assert issubclass(GtkNotAvailableError, RuntimeError)

    def test_require_gtk_raises_when_unavailable(self):
        from gateos_manager.ui import GtkNotAvailableError, require_gtk
        import gateos_manager.ui as _ui

        original = _ui.GTK_AVAILABLE
        try:
            _ui.GTK_AVAILABLE = False
            with self.assertRaises(GtkNotAvailableError):
                require_gtk()
        finally:
            _ui.GTK_AVAILABLE = original

    def test_require_gtk_passes_when_available(self):
        from gateos_manager.ui import require_gtk
        import gateos_manager.ui as _ui

        _ui.GTK_AVAILABLE = True
        require_gtk()  # must not raise


class TestGateOSAPI(unittest.TestCase):
    """Unit tests for GateOSAPI HTTP client (no real network)."""

    def _make_response(self, data, status=200):
        body = json.dumps(data).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("gateos_manager.ui.api_client.urllib.request.urlopen")
    def test_list_environments_returns_list(self, mock_urlopen):
        mock_urlopen.return_value = self._make_response([{"name": "dev"}, {"name": "gaming"}])
        api = GateOSAPI(base_url="http://localhost:8088", token="tok")
        result = api.list_environments()
        assert len(result) == 2
        assert result[0]["name"] == "dev"

    @patch("gateos_manager.ui.api_client.urllib.request.urlopen")
    def test_switch_environment_posts_correct_path(self, mock_urlopen):
        mock_urlopen.return_value = self._make_response({"status": "ok"})
        api = GateOSAPI(base_url="http://localhost:8088", token="tok")
        result = api.switch_environment("gaming")
        assert result["status"] == "ok"
        call_req = mock_urlopen.call_args[0][0]
        assert "/switch/gaming" in call_req.full_url

    @patch("gateos_manager.ui.api_client.urllib.request.urlopen")
    def test_health_endpoint(self, mock_urlopen):
        mock_urlopen.return_value = self._make_response({"status": "healthy"})
        api = GateOSAPI(base_url="http://localhost:8088")
        result = api.health()
        assert result["status"] == "healthy"

    @patch("gateos_manager.ui.api_client.urllib.request.urlopen", side_effect=OSError("refused"))
    def test_connection_error_raises_api_error(self, _mock):
        api = GateOSAPI(base_url="http://localhost:8088")
        with self.assertRaises(APIError) as ctx:
            api.list_environments()
        assert "Connection error" in str(ctx.exception)

    def test_token_in_auth_header(self):
        api = GateOSAPI(base_url="http://localhost:8088", token="secret-token")
        headers = api._headers()
        assert headers["Authorization"] == "Bearer secret-token"

    def test_no_token_no_auth_header(self):
        import os as _os
        # Temporarily clear the env var so the fallback doesn't pick it up
        saved = _os.environ.pop("GATEOS_API_TOKEN", None)
        try:
            api = GateOSAPI(base_url="http://localhost:8088", token="")
            headers = api._headers()
            assert "Authorization" not in headers
        finally:
            if saved is not None:
                _os.environ["GATEOS_API_TOKEN"] = saved

    def test_base_url_trailing_slash_stripped(self):
        api = GateOSAPI(base_url="http://localhost:8088/", token="")
        assert not api.base_url.endswith("/")


class TestEnvListPanel(unittest.TestCase):
    def _make_api(self, envs=None, fail=False):
        api = MagicMock(spec=GateOSAPI)
        if fail:
            api.list_environments.side_effect = APIError("connection refused")
        else:
            api.list_environments.return_value = envs or []
        return api

    def test_refresh_with_environments(self):
        envs = [
            {"metadata": {"name": "dev", "description": "Development"}, "spec": {"category": "dev"}},
            {"metadata": {"name": "gaming", "description": "Gaming"}, "spec": {"category": "gaming"}},
        ]
        api = self._make_api(envs=envs)
        panel = EnvListPanel(api)
        panel.refresh()
        assert len(panel._rows) == 2

    def test_refresh_empty_shows_placeholder(self):
        api = self._make_api(envs=[])
        panel = EnvListPanel(api)
        panel.refresh()
        assert len(panel._rows) == 1  # placeholder row

    def test_refresh_api_error_shows_error_row(self):
        api = self._make_api(fail=True)
        panel = EnvListPanel(api)
        panel.refresh()
        assert len(panel._rows) == 1  # error row

    def test_refresh_clears_old_rows(self):
        api = self._make_api(envs=[{"metadata": {"name": "dev"}, "spec": {}}])
        panel = EnvListPanel(api)
        panel.refresh()
        panel.refresh()  # second refresh should not double-add
        assert len(panel._rows) == 1


class TestSwitchButton(unittest.TestCase):
    def _make_api(self, fail=False):
        api = MagicMock(spec=GateOSAPI)
        if fail:
            api.switch_environment.side_effect = APIError("timeout")
        else:
            api.switch_environment.return_value = {"status": "ok"}
        return api

    def test_set_target_env_updates_button(self):
        api = self._make_api()
        btn = SwitchButton(api)
        btn.set_target_env("gaming")
        assert btn._target == "gaming"

    def test_set_current_env_updates_label(self):
        api = self._make_api()
        btn = SwitchButton(api)
        btn.set_current_env("dev")
        assert "Dev" in btn._status_label.get_label() or "dev" in btn._status_label.get_label()

    def test_set_current_env_empty_shows_dash(self):
        api = self._make_api()
        btn = SwitchButton(api)
        btn.set_current_env("")
        assert "No environment active" in btn._status_label.get_label()

    def test_switch_success_calls_api(self):
        api = self._make_api()
        btn = SwitchButton(api)
        btn._target = "gaming"
        btn._do_switch()
        api.switch_environment.assert_called_once_with("gaming")

    def test_switch_failure_emits_switch_failed(self):
        """Verify _do_switch handles failures by calling _on_switch_error."""
        api = self._make_api(fail=True)
        btn = SwitchButton(api)
        btn._target = "gaming"
        # Patch emit to capture calls (GObject signals are mocked)
        emitted: list[tuple] = []
        btn.emit = lambda sig, *a: emitted.append((sig, *a))
        btn._do_switch()
        # The API must have been called
        api.switch_environment.assert_called_once_with("gaming")
        # emit("switch-failed", name, error) must have been called
        assert any(e[0] == "switch-failed" for e in emitted), f"No switch-failed emitted; got {emitted}"

    def test_no_switch_when_no_target(self):
        api = self._make_api()
        btn = SwitchButton(api)
        btn._target = ""
        btn._on_switch_clicked(MagicMock())
        api.switch_environment.assert_not_called()

    def test_no_switch_when_busy(self):
        api = self._make_api()
        btn = SwitchButton(api)
        btn._target = "dev"
        btn._busy = True
        btn._on_switch_clicked(MagicMock())
        api.switch_environment.assert_not_called()


class TestStatusBar(unittest.TestCase):
    def _make_api(self, healthy=True):
        api = MagicMock(spec=GateOSAPI)
        if not healthy:
            api.health.side_effect = APIError("offline")
        else:
            api.health.return_value = {"status": "ok"}
        return api

    def test_set_active_env_updates_label(self):
        api = self._make_api()
        bar = StatusBar(api)
        bar.set_active_env("dev")
        assert "Dev" in bar._env_label.get_label() or "dev" in bar._env_label.get_label()

    def test_set_active_env_empty(self):
        api = self._make_api()
        bar = StatusBar(api)
        bar.set_active_env("")
        assert "—" in bar._env_label.get_label()

    def test_check_api_healthy(self):
        api = self._make_api(healthy=True)
        bar = StatusBar(api)
        bar._check_api()
        assert "connected" in bar._api_status.get_label()

    def test_check_api_offline(self):
        api = self._make_api(healthy=False)
        bar = StatusBar(api)
        bar._check_api()
        assert "offline" in bar._api_status.get_label()

    def test_stop_polling_removes_timer(self):
        api = self._make_api()
        bar = StatusBar(api)
        bar._timer_id = 99
        bar.stop_polling()
        assert bar._timer_id is None


class TestAppIndicatorTray(unittest.TestCase):
    def test_tray_unavailable_when_no_appindicator(self):
        api = MagicMock(spec=GateOSAPI)
        with patch("gateos_manager.ui.tray._INDICATOR_AVAILABLE", False):
            tray = AppIndicatorTray(api)
        assert not tray.available

    def test_set_environments_no_crash_when_unavailable(self):
        api = MagicMock(spec=GateOSAPI)
        with patch("gateos_manager.ui.tray._INDICATOR_AVAILABLE", False):
            tray = AppIndicatorTray(api)
        tray.set_environments([{"metadata": {"name": "dev"}}])  # must not raise

    def test_set_active_env_no_crash_when_unavailable(self):
        api = MagicMock(spec=GateOSAPI)
        with patch("gateos_manager.ui.tray._INDICATOR_AVAILABLE", False):
            tray = AppIndicatorTray(api)
        tray.set_active_env("gaming")  # must not raise


class TestMainEntryPoint(unittest.TestCase):
    def test_no_display_flag_exits_zero(self):
        with patch.dict("os.environ", {"GATEOS_UI_NO_DISPLAY": "1"}):
            from gateos_manager.ui.app import main
            result = main([])
        assert result == 0

    def test_app_id_constant(self):
        from gateos_manager.ui import APP_ID
        assert APP_ID == "io.gateos.Manager"

    def test_api_url_default(self):
        import os
        os.environ.pop("GATEOS_API_URL", None)
        import importlib
        import gateos_manager.ui as _ui_mod
        importlib.reload(_ui_mod)
        assert "127.0.0.1" in _ui_mod.API_URL or "localhost" in _ui_mod.API_URL


class TestGateOSWindow(unittest.TestCase):
    """Tests for GateOSWindow construction and all callbacks."""

    def _make_window(self, env_list=None):
        mock_api = MagicMock()
        mock_api.list_environments.return_value = env_list or []
        mock_api.health.return_value = {"status": "ok"}
        app = GateOSApp.__new__(GateOSApp)
        # Required attribute for ApplicationWindow ctor
        app._window = None
        with patch("gateos_manager.ui.app.GateOSAPI", return_value=mock_api):
            window = GateOSWindow(app)
        return window, mock_api

    def test_window_construction_no_crash(self):
        window, _ = self._make_window()
        assert window is not None

    def test_initial_load_calls_refresh(self):
        # GLib.idle_add immediately calls _initial_load → env_list.refresh()
        _, mock_api = self._make_window()
        mock_api.list_environments.assert_called()

    def test_on_refresh_triggers_env_list_refresh(self):
        window, mock_api = self._make_window()
        mock_api.list_environments.reset_mock()
        window._on_refresh(MagicMock())
        mock_api.list_environments.assert_called()

    def test_on_env_selected_sets_switch_target(self):
        window, _ = self._make_window()
        window._on_env_selected(None, "gaming")
        assert window._switch_btn._target == "gaming"

    def test_on_switch_done_updates_status_bar(self):
        window, _ = self._make_window()
        window._on_switch_done(None, "dev")
        label = window._status_bar._env_label.get_label()
        assert "Dev" in label or "dev" in label

    def test_on_switch_done_updates_tray(self):
        window, _ = self._make_window()
        # Tray is unavailable in CI; set_active_env should be a no-op
        window._on_switch_done(None, "gaming")  # must not raise

    def test_close_request_stops_polling(self):
        window, _ = self._make_window()
        window._status_bar._timer_id = 99
        result = window.do_close_request()
        assert result is False
        assert window._status_bar._timer_id is None


class TestGateOSApp(unittest.TestCase):
    """Tests for GateOSApp lifecycle methods."""

    def _patched_api(self):
        mock_api = MagicMock()
        mock_api.list_environments.return_value = []
        mock_api.health.return_value = {"status": "ok"}
        return mock_api

    def test_do_activate_creates_window(self):
        app = GateOSApp()
        assert app._window is None
        with patch("gateos_manager.ui.app.GateOSAPI", return_value=self._patched_api()):
            app.do_activate()
        assert app._window is not None

    def test_do_activate_reuses_existing_window(self):
        app = GateOSApp()
        mock_api = self._patched_api()
        with patch("gateos_manager.ui.app.GateOSAPI", return_value=mock_api):
            app.do_activate()
            w1 = app._window
            app.do_activate()
            w2 = app._window
        assert w1 is w2

    def test_do_startup_no_crash(self):
        app = GateOSApp()
        # Should not raise
        app.do_startup()

    def test_main_no_display_mode(self):
        with patch.dict("os.environ", {"GATEOS_UI_NO_DISPLAY": "1"}):
            from gateos_manager.ui.app import main
            assert main([]) == 0

    def test_main_default_runs_app(self):
        """main() without display flag creates GateOSApp and calls run()."""
        import os as _os
        env = {k: v for k, v in _os.environ.items() if k != "GATEOS_UI_NO_DISPLAY"}
        with patch.dict("os.environ", env, clear=True):
            with patch("gateos_manager.ui.app.GateOSAPI", return_value=self._patched_api()):
                from gateos_manager.ui.app import main
                result = main(["gateos-ui"])
        assert result == 0  # mock Adw.Application.run() returns 0


class TestAppIndicatorTrayWithIndicator(unittest.TestCase):
    """Test AppIndicatorTray code paths that run when indicator IS available."""

    def _make_tray_with_indicator(self):
        api = MagicMock(spec=GateOSAPI)
        with patch("gateos_manager.ui.tray._INDICATOR_AVAILABLE", False):
            tray = AppIndicatorTray(api)
        tray._indicator = MagicMock()
        tray.available = True
        return tray

    def test_set_environments_calls_build_menu(self):
        tray = self._make_tray_with_indicator()
        tray.set_environments([{"metadata": {"name": "dev"}}])
        tray._indicator.set_menu.assert_called_once()

    def test_set_environments_empty_builds_quit_only_menu(self):
        tray = self._make_tray_with_indicator()
        tray.set_environments([])
        tray._indicator.set_menu.assert_called_once()

    def test_set_active_env_calls_indicator_set_label(self):
        tray = self._make_tray_with_indicator()
        tray.set_active_env("gaming")
        tray._indicator.set_label.assert_called_once()
        label_arg = tray._indicator.set_label.call_args[0][0]
        assert "Gaming" in label_arg

    def test_set_active_env_none_indicator_no_crash(self):
        api = MagicMock(spec=GateOSAPI)
        with patch("gateos_manager.ui.tray._INDICATOR_AVAILABLE", False):
            tray = AppIndicatorTray(api)
        tray.set_active_env("dev")  # _indicator is None → should not raise

    def test_build_menu_with_envs(self):
        tray = self._make_tray_with_indicator()
        envs = [{"metadata": {"name": "dev"}}, {"name": "gaming"}]
        tray._build_menu(envs=envs)
        tray._indicator.set_menu.assert_called_once()

    def test_build_menu_without_envs(self):
        tray = self._make_tray_with_indicator()
        tray._build_menu()
        tray._indicator.set_menu.assert_called_once()

    def test_on_menu_activate_emits_env_selected(self):
        tray = self._make_tray_with_indicator()
        emitted: list = []
        tray.emit = lambda sig, *a: emitted.append((sig, *a))
        tray._on_menu_activate(MagicMock(), "dev")
        assert ("env-selected", "dev") in emitted

    def test_on_quit_calls_sys_exit(self):
        tray = self._make_tray_with_indicator()
        with patch("sys.exit") as mock_exit:
            tray._on_quit(MagicMock())
        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
