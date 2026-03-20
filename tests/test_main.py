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
    enabled_calls = []
    # worker calls enable(); simulate it being triggered
    main._sleep_enabled.clear()  # start disabled

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_sleep(fake_icon, None)

    assert main._sleep_enabled.is_set()


def test_toggle_sleep_disable_error_is_logged(monkeypatch):
    import main
    errors = []
    main._sleep_enabled.set()

    monkeypatch.setattr(main.sleep_control, "disable", lambda: (_ for _ in ()).throw(OSError("fail")))
    monkeypatch.setattr(main.logger, "error", lambda msg: errors.append(msg))

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_sleep(fake_icon, None)  # must not raise

    assert any("fail" in str(e) for e in errors)


# ── toggle_autostart ──────────────────────────────────────────────────────────

def test_toggle_autostart_enable(monkeypatch):
    import main
    main.auto = False
    enabled_calls = []
    monkeypatch.setattr(main.autostart, "enable", lambda: enabled_calls.append(1))

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_autostart(fake_icon, None)

    assert main.auto is True
    assert len(enabled_calls) == 1


def test_toggle_autostart_error_does_not_flip_state(monkeypatch):
    import main
    main.auto = False
    monkeypatch.setattr(main.autostart, "enable", lambda: (_ for _ in ()).throw(RuntimeError("not frozen")))

    fake_icon = types.SimpleNamespace(update_menu=lambda: None)
    main.toggle_autostart(fake_icon, None)  # must not raise

    assert main.auto is False  # state must not have flipped


# ── load_icon ─────────────────────────────────────────────────────────────────

def test_load_icon_uses_fallback_when_file_missing(monkeypatch, tmp_path):
    import main
    # Point base_path to an empty temp dir so icon.ico does not exist
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.setattr(main.os.path, "abspath", lambda f: str(tmp_path / "main.py"))

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
    monkeypatch.setattr(main.os.path, "abspath", lambda f: str(tmp_path / "main.py"))
    monkeypatch.setattr(main.Image, "open", fake_open, raising=False)

    img = main.load_icon()
    assert len(opened) == 1
    assert isinstance(img, FakeImg)
