import sys
import winreg

APP_NAME = "NoSleep"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def enable():
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Autostart can only be enabled for the packaged EXE, not when running from source.")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.executable)


def disable():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return value == sys.executable
    except FileNotFoundError:
        return False
