[Back to README](../README.md) · [Architecture →](architecture.md)

# Getting Started

## Prerequisites

- **Windows 10 / 11**
- **Python 3.12**
- [**uv**](https://github.com/astral-sh/uv) package manager

## Installation

```bash
git clone https://github.com/daniel-perebinos/NoSleep.git
cd NoSleep
uv sync
```

## Running

```bash
uv run python src/main.py
```

A tray icon appears in the system notification area. Right-click it to:

| Menu Item | Action |
|-----------|--------|
| **Prevent Sleep** | Toggle sleep prevention on/off (checked = active) |
| **Autostart** | Toggle Windows startup entry (only visible in packaged EXE) |
| **Exit** | Disable sleep prevention and close the app |

Sleep prevention is **enabled by default** when the app starts.

## Logs

Logs are written to `%LOCALAPPDATA%\NoSleep\logs\app.log`:

| Setting | Value |
|---------|-------|
| Rotation | 1 MB per file |
| Retention | 7 days |
| Console output | INFO level (only when running from source) |
| File output | DEBUG level |

To view logs:

```powershell
Get-Content "$env:LOCALAPPDATA\NoSleep\logs\app.log" -Tail 20
```

## See Also

- [Architecture](architecture.md) — how the code is structured
- [Building](building.md) — build standalone EXE and installer
