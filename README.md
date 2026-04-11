# 💤 NoSleep

<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-2ea44f?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-blueviolet?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/daniel-perebinos/NoSleep/ci.yml?style=for-the-badge&label=CI)

**A lightweight Windows system tray utility that keeps your PC awake — without touching your power settings.**

[⬇️ Download](#-download) · [🚀 Quick Start](#-quick-start) · [📖 Documentation](#-documentation)

</div>

---

## ✨ What is NoSleep?

NoSleep sits quietly in your **system tray** and prevents Windows from sleeping or hibernating by using the native `SetThreadExecutionState` API — no admin rights, no power plan changes, completely reversible.

| Use Case | Why NoSleep helps |
|---|---|
| ⬇️ Long downloads | Keeps the PC awake until it's done |
| 🎤 Presentations | No more screen blanking mid-slide |
| 🧑‍💻 Remote sessions | Keeps RDP / SSH connections alive |
| 🎬 Media playback | Prevents interruptions during videos |

---

## 🌟 Key Features

- 🖥️ **Minimalist UI** — lives entirely in the system tray, zero clutter
- 💤 **One-click toggle** — enable/disable sleep prevention instantly
- ⚡ **Autostart with Windows** — optional, toggled from the tray menu
- 🔒 **Single instance** — socket lock on port 47200 prevents duplicates
- 🧾 **Smart logging** — Loguru with rotation & 7-day retention in `%LOCALAPPDATA%`
- 🧭 **Modern codebase** — Python `pathlib`, clean architecture, fully tested

---

## ⬇️ Download

Head to the [**Releases**](../../releases) page and grab the latest:

| File | Description |
|---|---|
| `NoSleepInstaller.exe` | ✅ Recommended — installs with shortcuts & uninstaller |
| `NoSleep.exe` | Portable standalone executable, no install needed |

---

## 🚀 Quick Start

```bash
git clone https://github.com/daniel-perebinos/NoSleep.git
cd NoSleep
uv sync
uv run python src/main.py
```

> Requires **Python 3.12** and [**uv**](https://github.com/astral-sh/uv). See [Getting Started](docs/getting-started.md) for full setup details.

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Installation, setup, logs |
| [Architecture](docs/architecture.md) | Module structure and runtime flow |
| [Building](docs/building.md) | Build standalone EXE and Windows installer |
| [Development](docs/development.md) | Linting, testing, contributing |

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/daniel-perebinos">Daniel Perebinos</a>
</div>
