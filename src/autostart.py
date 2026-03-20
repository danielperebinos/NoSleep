import sys
import winreg

APP_NAME = "NoSleep"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def enable():
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Autostart can only be enabled for the packaged EXE, not when running from source.")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.executable)
    # Log the written path so it is auditable if the EXE is later moved
    from loguru import logger
    logger.info(f"Autostart enabled: {sys.executable}")


def disable():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except OSError:
        # FileNotFoundError (key absent) is expected; PermissionError and other
        # OSError subclasses are also swallowed — nothing to undo in that case.
        pass


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return value == sys.executable
    except OSError:
        return False
