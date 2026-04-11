# Project: NoSleep

## Overview
A Windows-only system tray application that prevents the PC from entering sleep or hibernation by periodically calling the Windows `SetThreadExecutionState` API — without modifying system-wide power settings. The app runs silently in the system tray with toggle controls for sleep prevention and autostart.

## Core Features
- Prevent system sleep/hibernation via `SetThreadExecutionState` API
- System tray icon with context menu for toggling sleep prevention
- Windows autostart management via Registry (`HKCU\...\Run`)
- Single-instance enforcement via socket lock on port 47200
- Structured logging to `%LOCALAPPDATA%\NoSleep\logs\` with rotation
- Standalone EXE packaging via PyInstaller
- Windows installer via Inno Setup

## Tech Stack
- **Language:** Python 3.12
- **UI:** pystray (system tray) + Pillow (icon rendering)
- **Windows API:** ctypes (kernel32.SetThreadExecutionState, winreg)
- **Logging:** loguru (file + console, rotation, retention)
- **Packaging:** PyInstaller (EXE), Inno Setup (installer)
- **Package Manager:** uv
- **Linting:** ruff (check + format)
- **Testing:** pytest + pytest-mock
- **CI/CD:** GitHub Actions (lint on Ubuntu, test + build on Windows)

## Architecture Notes
- Three-module design: `main.py` (orchestrator), `sleep_control.py` (Win API wrapper), `autostart.py` (Registry management)
- Background daemon thread sends heartbeat every 30 seconds via `threading.Event` wait
- Global state managed through `threading.Event` objects (`sleep_enabled`, `auto`, `wake_event`)
- Worker thread has circuit-breaker pattern: disables after 5 consecutive failures
- Autostart menu item only shown when running as frozen EXE

## Architecture
See `.ai-factory/ARCHITECTURE.md` for detailed architecture guidelines.
Pattern: Layered Architecture

## Non-Functional Requirements
- Logging: loguru with DEBUG to file, INFO to console (source mode only)
- Error handling: try/except with loguru logging, graceful degradation
- Security: No elevated privileges required, per-user Registry key only
- Platform: Windows-only (ctypes.windll, winreg)
