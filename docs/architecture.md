[← Getting Started](getting-started.md) · [Back to README](../README.md) · [Building →](building.md)

# Architecture

NoSleep has three source files, each owning a distinct layer of responsibility.

## Source Layout

```
src/
├── main.py           # Entry point, logging setup, tray icon loop
├── sleep_control.py  # ctypes wrapper for SetThreadExecutionState
├── autostart.py      # Windows Registry autostart key management
└── icon.ico          # System tray icon asset
```

## Module Responsibilities

| Module | Layer | Responsibility |
|--------|-------|---------------|
| `main.py` | Presentation + Orchestration | Loguru logging, single-instance socket lock (port 47200), daemon worker thread, pystray tray icon event loop |
| `sleep_control.py` | Service | `enable()` sets `ES_CONTINUOUS \| ES_SYSTEM_REQUIRED \| ES_DISPLAY_REQUIRED`; `disable()` resets to `ES_CONTINUOUS` |
| `autostart.py` | Service | Reads/writes `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |

## Dependency Flow

```
main.py (presentation + orchestration)
   ├── sleep_control.py (service — stateless)
   └── autostart.py (service — stateless)
```

Service modules never import from `main.py` or from each other. All mutable state lives in `main.py` as `threading.Event` objects.

## Runtime Flow

```
Startup → setup_logging() → socket lock → autostart check
                                         ↓
                              worker thread (daemon)
                              └── enable() every 30s while sleep_enabled is set
                                         ↓
                              Tray menu toggle → update Event → wake worker → re-render menu
                                         ↓
                              On exit → disable() → close socket → cleanup
```

The worker thread uses a `wake_event` with 30-second timeout. Toggling sleep prevention calls `wake_event.set()` so the change takes effect immediately rather than waiting for the next cycle.

## Error Handling

- **Service modules** raise `RuntimeError` or `OSError` on failure
- **`main.py`** catches exceptions, logs them, and decides whether to degrade gracefully
- The worker has a **circuit breaker**: after 5 consecutive `enable()` failures, it auto-disables sleep prevention

## See Also

- [Getting Started](getting-started.md) — installation and usage
- [Building](building.md) — packaging into EXE and installer
