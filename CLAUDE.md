# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NoSleep** is a Windows-only system tray application that prevents the PC from sleeping or hibernating using the Windows `SetThreadExecutionState` API — without changing system-wide power settings.

## Development Commands

This project uses `uv` for dependency management (Python 3.12 required).

```bash
# Install dependencies
uv sync

# Run from source
uv run python src/main.py

# Lint
uv run ruff check .
uv run ruff format .

# Build standalone EXE
uv run pyinstaller --onefile --noconsole --icon=src/icon.ico --add-data "src/icon.ico;." --name NoSleep src/main.py
```

## Packaging / Installer

After building the EXE, create the Windows installer using [Inno Setup](https://jrsoftware.org/isinfo.php):

1. Build the EXE first (output goes to `dist/NoSleep.exe`)
2. Open `installer.iss` in Inno Setup Compiler and compile — outputs `NoSleepInstaller.exe`

## Architecture

The app has three source files with distinct responsibilities:

- **`main.py`** — Entry point and orchestrator. Sets up logging (loguru → `%LOCALAPPDATA%\NoSleep\logs\app.log`), enforces single-instance via a socket lock on port 47200, starts a daemon worker thread, and runs the `pystray` tray icon event loop.
- **`sleep_control.py`** — Thin wrapper around the Windows `SetThreadExecutionState` API via `ctypes`. `enable()` sets `ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED`; `disable()` resets to `ES_CONTINUOUS`.
- **`autostart.py`** — Manages the Windows autostart Registry key at `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.

**Runtime flow:** The worker thread calls `sleep_control.enable()` every 30 seconds while `enabled` is `True`. Toggling sleep prevention or autostart from the tray menu updates the global state and re-renders the menu checkmarks. On exit, `sleep_control.disable()` is called to restore normal sleep behavior.
