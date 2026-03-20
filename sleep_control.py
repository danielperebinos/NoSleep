import ctypes

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def enable():
    result = ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )
    if result == 0:
        raise RuntimeError("SetThreadExecutionState failed (returned 0)")


def disable():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
