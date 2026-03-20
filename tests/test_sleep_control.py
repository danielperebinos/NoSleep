"""Tests for sleep_control.py — mocks ctypes.windll so no Windows API is called."""
import sys
import types
import pytest


def _make_windll_mock(return_value: int):
    """Build a minimal ctypes mock that returns `return_value` from SetThreadExecutionState."""
    kernel32 = types.SimpleNamespace(SetThreadExecutionState=lambda flags: return_value)
    windll = types.SimpleNamespace(kernel32=kernel32)
    return windll


@pytest.fixture(autouse=True)
def patch_ctypes(monkeypatch):
    """Inject a fake ctypes.windll before every test and reload sleep_control."""
    import ctypes
    windll = _make_windll_mock(return_value=1)  # default: success
    monkeypatch.setattr(ctypes, "windll", windll)
    # Re-import so the module picks up the patched windll
    import importlib
    import sleep_control
    importlib.reload(sleep_control)
    return windll


def test_enable_success(monkeypatch):
    import ctypes, importlib, sleep_control
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: 1
    importlib.reload(sleep_control)
    sleep_control.enable()  # should not raise


def test_enable_raises_on_zero(monkeypatch):
    import ctypes, importlib, sleep_control
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: 0
    importlib.reload(sleep_control)
    with pytest.raises(RuntimeError, match="SetThreadExecutionState failed"):
        sleep_control.enable()


def test_disable_success(monkeypatch):
    import ctypes, importlib, sleep_control
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: 1
    importlib.reload(sleep_control)
    sleep_control.disable()  # should not raise


def test_disable_raises_on_zero(monkeypatch):
    import ctypes, importlib, sleep_control
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: 0
    importlib.reload(sleep_control)
    with pytest.raises(RuntimeError, match="SetThreadExecutionState"):
        sleep_control.disable()
