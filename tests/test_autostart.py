"""Tests for autostart.py — mocks winreg so no registry is touched."""

import sys
import pytest


@pytest.fixture(autouse=True)
def mock_winreg(monkeypatch):
    """Replace winreg with a minimal in-memory stub before each test."""
    import types

    _store: dict[str, str] = {}

    HKEY_CURRENT_USER = 0x80000001
    KEY_SET_VALUE = 0x0002
    KEY_READ = 0x20019
    REG_SZ = 1

    class FakeKey:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def OpenKey(hive, path, reserved=0, access=0):
        return FakeKey()

    def SetValueEx(key, name, reserved, reg_type, value):
        _store[name] = value

    def QueryValueEx(key, name):
        if name not in _store:
            raise FileNotFoundError
        return (_store[name], REG_SZ)

    def DeleteValue(key, name):
        if name not in _store:
            raise FileNotFoundError
        del _store[name]

    fake_winreg = types.ModuleType("winreg")
    fake_winreg.HKEY_CURRENT_USER = HKEY_CURRENT_USER
    fake_winreg.KEY_SET_VALUE = KEY_SET_VALUE
    fake_winreg.KEY_READ = KEY_READ
    fake_winreg.REG_SZ = REG_SZ
    fake_winreg.OpenKey = OpenKey
    fake_winreg.SetValueEx = SetValueEx
    fake_winreg.QueryValueEx = QueryValueEx
    fake_winreg.DeleteValue = DeleteValue

    monkeypatch.setitem(sys.modules, "winreg", fake_winreg)

    import importlib
    import autostart

    importlib.reload(autostart)

    return _store


def test_is_enabled_false_when_key_absent():
    import autostart

    assert autostart.is_enabled() is False


def test_enable_and_is_enabled(monkeypatch, mock_winreg):
    import autostart

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    autostart.enable()
    assert mock_winreg["NoSleep"] == sys.executable
    assert autostart.is_enabled() is True


def test_is_enabled_false_for_wrong_path(monkeypatch, mock_winreg):
    import autostart

    mock_winreg["NoSleep"] = "/some/other/path/nosleep.exe"
    assert autostart.is_enabled() is False


def test_disable_removes_key(monkeypatch, mock_winreg):
    import autostart

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    autostart.enable()
    autostart.disable()
    assert autostart.is_enabled() is False


def test_disable_is_idempotent():
    import autostart

    # Calling disable when the key is absent should not raise
    autostart.disable()
    autostart.disable()


def test_enable_raises_when_not_frozen():
    import autostart

    # sys.frozen is not set in the test runner
    with pytest.raises(RuntimeError, match="packaged EXE"):
        autostart.enable()


def test_disable_survives_permission_error(monkeypatch, mock_winreg):
    import autostart
    import winreg

    def raise_permission_error(*a, **kw):
        raise PermissionError("access denied")

    monkeypatch.setattr(winreg, "OpenKey", raise_permission_error)
    autostart.disable()  # must not raise


def test_is_enabled_returns_false_on_permission_error(monkeypatch, mock_winreg):
    import autostart
    import winreg

    def raise_permission_error(*a, **kw):
        raise PermissionError("access denied")

    monkeypatch.setattr(winreg, "OpenKey", raise_permission_error)
    assert autostart.is_enabled() is False
