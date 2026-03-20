# 💤 NoSleep

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)

**NoSleep** is a lightweight, modern Windows tray utility that prevents your PC from entering **sleep** or **hibernation
** — without changing system-wide power settings.

Perfect for:

- ⬇️ long downloads
- 🎤 presentations
- 🧑‍💻 keeping remote/active sessions alive

---

## ✨ Key Features

|                                                                            |                                                                              |
|----------------------------------------------------------------------------|------------------------------------------------------------------------------|
| 🖥️ **Minimalist UI**<br/>Runs entirely in the **System Tray**.            | 💤 **Smart Sleep Prevention**<br/>Toggle protection with a **single click**. |
| ⚡ **Windows Autostart**<br/>Start with Windows (optional).                 | 🔒 **Single Instance**<br/>Socket lock ensures only **one instance**.        |
| 🧾 **Robust Logging**<br/>Loguru + rotation/retention in `%LOCALAPPDATA%`. | 🧭 **Modern Paths**<br/>Powered by Python `pathlib`.                         |

## 🚀 Getting Started

### 1) Requirements

- **Windows 10 / 11**
- **Python 3.9+** (if running from source)
- Dependencies:
    - `pystray`
    - `Pillow`
    - `loguru`

### 2) Run from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/nosleep.git
cd nosleep

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
````

---

## 🛠️ Build a Standalone Executable (EXE)

To create a standalone `.exe` that runs quietly (no console) and uses your custom icon, build with **PyInstaller**:

```bash
pyinstaller --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." --name NoSleep main.py
```

> [!TIP]
> The `--noconsole` flag is crucial for tray applications to prevent a Command Prompt window from popping up.

---

## 📂 Logs & Data

To comply with Windows security standards and avoid permission issues, NoSleep stores logs under the user’s local app
data folder.

| Item         | Location                       |
|--------------|--------------------------------|
| Log Folder   | `%LOCALAPPDATA%\NoSleep\logs\` |
| Log Rotation | `1 MB` per file                |
| Retention    | `7 days`                       |

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create your feature branch

   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes

   ```bash
   git commit -m "Add some AmazingFeature"
   ```
4. Push to the branch

   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
