"""Tests for main.py logic — state transitions, icon loading, error paths."""
import sys
import os
import threading
import types
import pytest


@pytest.fixture(autouse=True)
def stub_external_modules(monkeypatch):
    """Stub pystray, PIL, sleep_control, autostart, loguru so main.py can be imported."""
    # pystray stubs
    class FakeMenu:
        SEPARATOR = object()
        def __init__(self, *items): pass

    class FakeMenuItem:
        def __init__(self, *args, **kwargs): pass

    class FakeIcon:
        def __init__(self, *args, **kwargs): pass
        def update_menu(self): pass
        def stop(self): pass
        def run(self): pass

    pystray_mod = types.ModuleType("pystray")
    pystray_mod.Icon = FakeIcon
    pystray_mod.Menu = FakeMenu
    pystray_mod.MenuItem = FakeMenuItem
    monkeypatch.setitem(sys.modules, "pystray", pystray_mod)

    # PIL stubs
    pil_mod = types.ModuleType("PIL")
    image_mod = types.ModuleType("PIL.Image")
    draw_mod = types.ModuleType("PIL.ImageDraw")

    class FakeImage:
        def __init__(self, *a, **kw): pass
        @staticmethod
        def new(*a, **kw): return FakeImage()
        @staticmethod
        def open(*a, **kw): return FakeImage()

    class FakeDraw:
        def __init__(self, *a, **kw): pass
        def ellipse(self, *a, **kw): pass
        def text(self, *a, **kw): pass

    image_mod.Image = FakeImage
    image_mod.open = FakeImage.open
    image_mod.new = FakeImage.new
    draw_mod.ImageDraw = FakeDraw
    draw_mod.Draw = lambda img: FakeDraw()

    pil_image = types.ModuleType("PIL.Image")
    pil_image.Image = FakeImage
    pil_image.open = FakeImage.open
    pil_image.new = FakeImage.new
    pil_draw = types.ModuleType("PIL.ImageDraw")
    pil_draw.Draw = lambda img: FakeDraw()

    monkeypatch.setitem(sys.modules, "PIL", pil_mod)
    monkeypatch.setitem(sys.modules, "PIL.Image", pil_image)
    monkeypatch.setitem(sys.modules, "PIL.ImageDraw", pil_draw)

    # sleep_control stub
    sc_mod = types.ModuleType("sleep_control")
    sc_mod.enable = lambda: None
    sc_mod.disable = lambda: None
    monkeypatch.setitem(sys.modules, "sleep_control", sc_mod)

    # autostart stub
    as_mod = types.ModuleType("autostart")
    as_mod.enable = lambda: None
    as_mod.disable = lambda: None
    as_mod.is_enabled = lambda: False
    monkeypatch.setitem(sys.modules, "autostart", as_mod)

    # winreg stub (needed on non-Windows)
    if "winreg" not in sys.modules:
        monkeypatch.setitem(sys.modules, "winreg", types.ModuleType("winreg"))

    # loguru stub
    class FakeLogger:
        def remove(self): pass
        def add(self, *a, **kw): pass
        def info(self, *a, **kw): pass
        def debug(self, *a, **kw): pass
        def warning(self, *a, **kw): pass
        def error(self, *a, **kw): pass
        def critical(self, *a, **kw): pass
        def exception(self, *a, **kw): pass

    loguru_mod = types.ModuleType("loguru")
    loguru_mod.logger = FakeLogger()
    monkeypatch.setitem(sys.modules, "loguru", loguru_mod)

    import importlib
    import main
    importlib.reload(main)


# ── toggle_sleep ──────────────────────────────────────────────────────────────

def test_toggle_sleep_disables(monkeypatch):
    import main
    disabled_calls = []
    monkeypatch.setattr(main.sleep_control, "disable", lambda: disabled_calls.append(1))

    main._sleep_enabled.set()  # start enabled

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_sleep(fake_icon, None)

    assert not main._sleep_enabled.is_set()
    assert len(disabled_calls) == 1


def test_toggle_sleep_enables(monkeypatch):
    import main
    main._sleep_enabled.clear()  # start disabled

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_sleep(fake_icon, None)

    assert main._sleep_enabled.is_set()


def test_toggle_sleep_disable_error_is_logged(monkeypatch):
    import main
    errors = []
    main._sleep_enabled.set()

    def raise_os_error():
        raise OSError("fail")

    monkeypatch.setattr(main.sleep_control, "disable", raise_os_error)
    monkeypatch.setattr(main.logger, "error", lambda msg: errors.append(msg))

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_sleep(fake_icon, None)  # must not raise

    assert any("fail" in str(e) for e in errors)


def test_toggle_sleep_disable_runtime_error_is_logged(monkeypatch):
    import main
    errors = []
    main._sleep_enabled.set()

    def raise_runtime_error():
        raise RuntimeError("api fail")

    monkeypatch.setattr(main.sleep_control, "disable", raise_runtime_error)
    monkeypatch.setattr(main.logger, "error", lambda msg: errors.append(msg))

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_sleep(fake_icon, None)  # must not raise

    assert any("api fail" in str(e) for e in errors)


# ── toggle_autostart ──────────────────────────────────────────────────────────

def test_toggle_autostart_enable(monkeypatch):
    import main
    main._auto.clear()
    enabled_calls = []
    monkeypatch.setattr(main.autostart, "enable", lambda: enabled_calls.append(1))

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_autostart(fake_icon, None)

    assert main._auto.is_set()
    assert len(enabled_calls) == 1


def test_toggle_autostart_error_does_not_flip_state(monkeypatch):
    import main
    main._auto.clear()

    def raise_not_frozen():
        raise RuntimeError("not frozen")

    monkeypatch.setattr(main.autostart, "enable", raise_not_frozen)

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_autostart(fake_icon, None)  # must not raise

    assert not main._auto.is_set()  # state must not have flipped


# ── load_icon ─────────────────────────────────────────────────────────────────

# ── check_single_instance ─────────────────────────────────────────────────────

def test_check_single_instance_acquires_lock(monkeypatch):
    import socket as _socket
    import main
    # Bind on an unused port to prove the lock is acquired
    bound_ports = []

    class FakeSocket:
        def setsockopt(self, *a): pass
        def bind(self, addr): bound_ports.append(addr[1])

    monkeypatch.setattr(main.socket, "socket", lambda *a, **kw: FakeSocket())
    main.instance_lock = None
    main.check_single_instance()
    assert main.INSTANCE_LOCK_PORT in bound_ports


def test_check_single_instance_exits_when_port_taken(monkeypatch):
    import socket as _socket
    import main

    class BusySocket:
        def setsockopt(self, *a): pass
        def bind(self, addr): raise _socket.error("address in use")

    monkeypatch.setattr(main.socket, "socket", lambda *a, **kw: BusySocket())
    with pytest.raises(SystemExit):
        main.check_single_instance()


# ── on_exit ───────────────────────────────────────────────────────────────────

def test_on_exit_closes_lock_and_stops_icon(monkeypatch):
    import main
    stopped = []
    closed = []

    class FakeLock:
        def close(self): closed.append(1)

    fake_icon = types.SimpleNamespace(stop=lambda: stopped.append(1))
    main.instance_lock = FakeLock()
    main.on_exit(fake_icon, None)

    assert len(stopped) == 1
    assert len(closed) == 1
    assert main.instance_lock is None


def test_on_exit_does_not_call_sleep_disable(monkeypatch):
    """disable() should NOT be called in on_exit — the finally block in main() handles it."""
    import main
    disable_calls = []
    monkeypatch.setattr(main.sleep_control, "disable", lambda: disable_calls.append(1))
    main.instance_lock = None
    fake_icon = types.SimpleNamespace(stop=lambda: None)
    main.on_exit(fake_icon, None)
    assert len(disable_calls) == 0


# ── create_menu ───────────────────────────────────────────────────────────────

def test_create_menu_no_autostart_when_not_frozen(monkeypatch):
    import main
    autostart_items = []

    class CapturingMenuItem:
        def __init__(self, label, *a, **kw):
            if label == "Autostart":
                autostart_items.append(label)

    monkeypatch.setattr(main, "MenuItem", CapturingMenuItem)
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    main.create_menu()
    assert len(autostart_items) == 0


def test_create_menu_has_autostart_when_frozen(monkeypatch):
    import main
    autostart_items = []

    class CapturingMenuItem:
        def __init__(self, label, *a, **kw):
            if label == "Autostart":
                autostart_items.append(label)

    monkeypatch.setattr(main, "MenuItem", CapturingMenuItem)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    main.create_menu()
    assert len(autostart_items) == 1


# ── setup_logging ─────────────────────────────────────────────────────────────

def test_setup_logging_falls_back_when_mkdir_fails(monkeypatch, tmp_path):
    import main
    from pathlib import Path

    def bad_mkdir(parents=False, exist_ok=False):
        raise OSError("no space left on device")

    warnings = []
    monkeypatch.setattr(main.logger, "warning", lambda msg: warnings.append(msg))
    monkeypatch.setattr(main.logger, "add", lambda *a, **kw: None)
    monkeypatch.setattr(main.logger, "remove", lambda: None)
    monkeypatch.setattr(main.logger, "info", lambda *a, **kw: None)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    # Patch Path.mkdir to raise
    original_mkdir = Path.mkdir
    monkeypatch.setattr(Path, "mkdir", lambda self, **kw: bad_mkdir(**kw))
    main.setup_logging()  # must not raise
    monkeypatch.setattr(Path, "mkdir", original_mkdir)

    assert any("File logging disabled" in str(w) for w in warnings)


# ── load_icon ─────────────────────────────────────────────────────────────────

def test_load_icon_uses_fallback_when_file_missing(monkeypatch, tmp_path):
    import main
    # Point __file__ to an empty temp dir so icon.ico does not exist
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.setattr(main, "__file__", str(tmp_path / "main.py"))

    img = main.load_icon()
    assert img is not None  # fallback image was created


def test_load_icon_returns_image_when_file_exists(monkeypatch, tmp_path):
    import main

    # Create a dummy icon.ico in tmp_path
    icon_path = tmp_path / "icon.ico"
    icon_path.write_bytes(b"\x00" * 16)  # placeholder bytes

    opened = []

    class FakeImg:
        pass

    def fake_open(path):
        opened.append(path)
        return FakeImg()

    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.setattr(main, "__file__", str(tmp_path / "main.py"))
    monkeypatch.setattr(main.Image, "open", fake_open, raising=False)

    img = main.load_icon()
    assert len(opened) == 1
    assert isinstance(img, FakeImg)
