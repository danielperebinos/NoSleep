"""Tests for sleep_control.py — mocks ctypes.windll so no Windows API is called."""
import sys
import types
import pytest

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


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
    import importlib
    import sleep_control
    importlib.reload(sleep_control)
    return windll


def test_enable_success():
    import sleep_control
    sleep_control.enable()  # should not raise


def test_enable_raises_on_zero(monkeypatch):
    import ctypes, importlib, sleep_control
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: 0
    importlib.reload(sleep_control)
    with pytest.raises(RuntimeError, match="SetThreadExecutionState failed"):
        sleep_control.enable()


def test_disable_success():
    import sleep_control
    sleep_control.disable()  # should not raise


def test_disable_raises_on_zero(monkeypatch):
    import ctypes, importlib, sleep_control
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: 0
    importlib.reload(sleep_control)
    with pytest.raises(RuntimeError, match="SetThreadExecutionState"):
        sleep_control.disable()


def test_enable_passes_correct_flags(monkeypatch):
    import ctypes, importlib, sleep_control
    calls = []
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: (calls.append(flags), 1)[1]
    importlib.reload(sleep_control)
    sleep_control.enable()
    assert calls == [ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED]


def test_disable_passes_only_es_continuous(monkeypatch):
    import ctypes, importlib, sleep_control
    calls = []
    ctypes.windll.kernel32.SetThreadExecutionState = lambda flags: (calls.append(flags), 1)[1]
    importlib.reload(sleep_control)
    sleep_control.disable()
    assert calls == [ES_CONTINUOUS]
