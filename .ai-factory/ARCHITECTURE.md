# Architecture: Layered Architecture

## Overview
NoSleep uses a simple layered architecture where each source module occupies a distinct responsibility layer. This is the natural fit for a small, focused Windows utility with a single feature domain (sleep prevention), a flat module structure, and no database or external services.

The architecture deliberately avoids over-engineering. With three source files and a single developer, formal abstractions like dependency injection containers or interface registries would add friction without value. The current module structure already implements clean layer separation organically.

## Decision Rationale
- **Project type:** Single-purpose Windows system tray utility
- **Tech stack:** Python 3.12, ctypes, pystray, loguru
- **Key factor:** Low complexity (3 modules, 1 feature) — a simple layered approach keeps the codebase navigable without ceremony

## Folder Structure
```
src/
├── main.py             # Presentation + Orchestration layer
│                       #   - System tray UI (pystray menu)
│                       #   - Logging setup
│                       #   - Single-instance enforcement
│                       #   - Worker thread lifecycle
├── sleep_control.py    # Service layer — Windows API wrapper
│                       #   - SetThreadExecutionState calls
│                       #   - Pure functions, no state
├── autostart.py        # Service layer — Registry wrapper
│                       #   - HKCU\...\Run key management
│                       #   - Pure functions, no state
└── icon.ico            # Static asset

tests/
├── test_main.py            # Tests for orchestration logic
├── test_sleep_control.py   # Tests for sleep API wrapper
└── test_autostart.py       # Tests for autostart management
```

## Layers

| Layer | Module(s) | Responsibility |
|-------|-----------|---------------|
| **Presentation** | `main.py` (tray menu, icon) | User-facing system tray UI and menu interactions |
| **Orchestration** | `main.py` (worker, state) | Thread management, global state (`threading.Event`), lifecycle |
| **Service** | `sleep_control.py`, `autostart.py` | Thin wrappers over Windows APIs, stateless |

## Dependency Rules

- `main.py` → `sleep_control.py` (calls `enable()`/`disable()`)
- `main.py` → `autostart.py` (calls `enable()`/`disable()`/`is_enabled()`)
- `sleep_control.py` → nothing (only stdlib `ctypes`)
- `autostart.py` → nothing (only stdlib `winreg` + `loguru`)

Dependency flow is strictly top-down:

```
main.py (presentation + orchestration)
   ├── sleep_control.py (service)
   └── autostart.py (service)
```

- Service modules NEVER import from `main.py`
- Service modules NEVER import from each other
- All global state lives in `main.py` only

## Key Principles

1. **Service modules are stateless** — `sleep_control` and `autostart` expose pure functions with no module-level mutable state. All coordination state (`sleep_enabled`, `auto`, `wake_event`) lives in `main.py`.

2. **Fail loudly at the boundary, recover gracefully at the top** — Service modules raise `RuntimeError` or `OSError` on failure. `main.py` catches and logs, deciding whether to degrade or halt.

3. **One module = one Windows subsystem** — Each service module wraps exactly one Windows API surface (`kernel32.SetThreadExecutionState` or `winreg`). If new Windows API integration is needed, add a new module rather than extending an existing one.

4. **No cross-module side effects** — Calling `sleep_control.enable()` only sets the execution state flag. It does not log, update UI, or modify global state. Side effects (logging, menu updates) belong to the caller in `main.py`.

## Code Examples

### Adding a new Windows API wrapper
When adding a new feature that touches a different Windows API (e.g., display brightness), create a new service module:

```python
# src/brightness_control.py
import ctypes

_dxva2 = ctypes.windll.dxva2

def set_brightness(level: int) -> None:
    """Set monitor brightness (0-100)."""
    # ... ctypes calls
    pass

def get_brightness() -> int:
    """Get current monitor brightness."""
    # ... ctypes calls
    pass
```

Then wire it into `main.py` — the service module stays stateless and independent.

### Correct error handling pattern
Service modules raise, orchestrator catches:

```python
# In sleep_control.py (service layer) — raise on failure
def enable():
    result = _tes(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
    if result == 0:
        raise RuntimeError("SetThreadExecutionState failed (returned 0)")

# In main.py (orchestration layer) — catch and decide
try:
    sleep_control.enable()
    consecutive_failures = 0
except Exception as e:
    consecutive_failures += 1
    logger.exception(f"Worker thread error: {e}")
```

## Anti-Patterns

- **Do not add state to service modules** — If you need to track whether sleep prevention is active, use a `threading.Event` in `main.py`, not a module-level boolean in `sleep_control.py`.
- **Do not import `main` from service modules** — This creates circular dependencies and breaks the layered structure.
- **Do not add abstraction layers prematurely** — No need for ABC interfaces, repository patterns, or DI frameworks at this project scale. If the project grows to 10+ modules, reconsider.
- **Do not merge service modules** — `sleep_control` and `autostart` should remain separate even though both are "Windows API wrappers". They serve different features and should be independently testable.
