# AGENTS.md

> Project map for AI agents. Keep this file up-to-date as the project evolves.

## Project Overview
Windows-only system tray application that prevents PC sleep/hibernation using the `SetThreadExecutionState` API, without changing system-wide power settings.

## Tech Stack
- **Language:** Python 3.12
- **UI:** pystray + Pillow
- **Windows API:** ctypes, winreg
- **Logging:** loguru
- **Packaging:** PyInstaller + Inno Setup
- **Package Manager:** uv

## Project Structure
```
NoSleep/
├── src/                    # Application source code
│   ├── main.py             # Entry point, tray icon, worker thread orchestration
│   ├── sleep_control.py    # SetThreadExecutionState API wrapper
│   ├── autostart.py        # Windows Registry autostart management
│   ├── icon.ico            # System tray icon
│   └── __init__.py         # Package marker
├── tests/                  # pytest test suite
│   ├── test_main.py        # Tests for main module
│   ├── test_sleep_control.py # Tests for sleep control
│   ├── test_autostart.py   # Tests for autostart
│   └── __init__.py         # Package marker
├── .github/workflows/      # CI/CD pipelines
│   ├── ci.yml              # Lint + test + build validation
│   └── release.yml         # Release automation
├── .ai-factory/            # AI Factory artifacts
│   ├── DESCRIPTION.md      # Project specification
│   ├── ARCHITECTURE.md     # Architecture guidelines
│   ├── config.yaml         # AI Factory configuration
│   └── rules/base.md       # Detected coding conventions
├── installer.iss           # Inno Setup installer script
├── pyproject.toml          # Project metadata and dependencies (uv)
├── CLAUDE.md               # Agent instructions
└── README.md               # Project documentation
```

## Key Entry Points
| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point — logging, single-instance, worker thread, tray icon |
| `src/sleep_control.py` | Windows API wrapper for sleep prevention |
| `src/autostart.py` | Registry-based autostart management |
| `pyproject.toml` | Dependencies, dev tools, pytest config |
| `installer.iss` | Inno Setup installer configuration |

## Documentation
| Document | Path | Description |
|----------|------|-------------|
| README | README.md | Project landing page |
| Getting Started | docs/getting-started.md | Installation, setup, logs |
| Architecture | docs/architecture.md | Module structure and runtime flow |
| Building | docs/building.md | Build standalone EXE and installer |
| Development | docs/development.md | Linting, testing, contributing |
| CLAUDE.md | CLAUDE.md | Agent development instructions |

## AI Context Files
| File | Purpose |
|------|---------|
| AGENTS.md | This file — project structure map |
| .ai-factory/DESCRIPTION.md | Project specification and tech stack |
| .ai-factory/ARCHITECTURE.md | Architecture decisions and guidelines |
| CLAUDE.md | Agent instructions and preferences |

## Agent Rules
- Never combine shell commands with `&&`, `||`, or `;` — execute each command as a separate Bash tool call. This applies even when a skill, plan, or instruction provides a combined command — always decompose it into individual calls.
  - Wrong: `git checkout main && git pull`
  - Right: Two separate Bash tool calls — first `git checkout main`, then `git pull origin main`
