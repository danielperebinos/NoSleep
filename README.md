# 💤 NoSleep

<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-2ea44f?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-blueviolet?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/daniel-perebinos/NoSleep/ci.yml?style=for-the-badge&label=CI)

**A lightweight Windows system tray utility that keeps your PC awake — without touching your power settings.**

[⬇️ Download Installer](#-download) · [🚀 Run from Source](#-run-from-source) · [🛠️ Build EXE](#%EF%B8%8F-build-a-standalone-executable)

</div>

---

## ✨ What is NoSleep?

NoSleep sits quietly in your **system tray** and prevents Windows from sleeping or hibernating by using the native `SetThreadExecutionState` API — no admin rights, no power plan changes, completely reversible.

Perfect for:

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

## 🚀 Run from Source

### Prerequisites

- Windows 10 / 11
- Python 3.12
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/daniel-perebinos/NoSleep.git
cd NoSleep

# Install dependencies
uv sync

# Run the app
uv run python src/main.py
```

---

## 🛠️ Build a Standalone Executable

```bash
uv run pyinstaller --onefile --noconsole --icon=src/icon.ico --add-data "src/icon.ico;." --name NoSleep src/main.py
```

> 💡 `--noconsole` is required for tray apps — it prevents a Command Prompt window from appearing.

The output EXE will be at `dist/NoSleep.exe`.

### 📦 Build the Windows Installer

After building the EXE, compile the installer with [Inno Setup](https://jrsoftware.org/isinfo.php):

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Output: `NoSleepInstaller.exe`

---

## 🏗️ Architecture

The app has three source files with distinct responsibilities:

```
src/
├── main.py           # Entry point, logging setup, tray icon loop
├── sleep_control.py  # ctypes wrapper for SetThreadExecutionState
└── autostart.py      # Windows Registry autostart key management
```

| File | Responsibility |
|---|---|
| `main.py` | Sets up loguru logging, enforces single-instance via socket lock (port 47200), starts daemon worker thread, runs pystray event loop |
| `sleep_control.py` | `enable()` sets `ES_CONTINUOUS \| ES_SYSTEM_REQUIRED \| ES_DISPLAY_REQUIRED`; `disable()` resets to `ES_CONTINUOUS` |
| `autostart.py` | Reads/writes `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |

**Runtime flow:**

```
Startup → socket lock → worker thread → enable() every 30s
                      ↓
              Tray menu toggle → update global state → re-render menu
                      ↓
              On exit → disable() → restore normal sleep behavior
```

---

## 📂 Logs & Data

| Item | Location |
|---|---|
| 📁 Log Folder | `%LOCALAPPDATA%\NoSleep\logs\` |
| 🔄 Log Rotation | `1 MB` per file |
| 🗑️ Retention | `7 days` |

---

## 🧪 Development

```bash
# Lint & format
uv run ruff check .
uv run ruff format .

# Run tests
uv run pytest
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. 🍴 Fork the project
2. 🌿 Create your feature branch: `git checkout -b feature/AmazingFeature`
3. 💾 Commit your changes: `git commit -m "Add AmazingFeature"`
4. 📤 Push to the branch: `git push origin feature/AmazingFeature`
5. 🔁 Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/daniel-perebinos">Daniel Perebinos</a>
</div>
