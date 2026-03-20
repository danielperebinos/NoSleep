import sys
import ctypes

if sys.platform != "win32":
    raise ImportError("sleep_control requires Windows")

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# SetThreadExecutionState returns DWORD (unsigned 32-bit); set restype accordingly
# so the return value is never misinterpreted as negative.
# Thread-affinity note: the execution state is per-calling-thread. Both enable()
# and disable() must be called from the same long-lived thread for the state
# to apply and be correctly reset.
_tes = ctypes.windll.kernel32.SetThreadExecutionState
_tes.restype = ctypes.c_uint32


def enable():
    result = _tes(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
    if result == 0:
        raise RuntimeError("SetThreadExecutionState failed (returned 0)")


def disable():
    result = _tes(ES_CONTINUOUS)
    if result == 0:
        raise RuntimeError("SetThreadExecutionState(ES_CONTINUOUS) failed (returned 0)")
