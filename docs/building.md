[← Architecture](architecture.md) · [Back to README](../README.md) · [Development →](development.md)

# Building

## Build a Standalone EXE

```bash
uv run pyinstaller --onefile --noconsole --icon=src/icon.ico --add-data "src/icon.ico;." --name NoSleep src/main.py
```

> `--noconsole` is required for tray apps — it prevents a Command Prompt window from appearing.

Output: `dist/NoSleep.exe`

## Build the Windows Installer

After building the EXE, compile the installer with [Inno Setup](https://jrsoftware.org/isinfo.php):

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Output: `NoSleepInstaller.exe`

The installer includes:
- Start Menu shortcut
- Desktop shortcut (optional)
- Uninstaller entry in Windows Settings

## CI/CD Pipelines

### CI (`ci.yml`)

Runs on every push and pull request:

1. Lints with ruff (Ubuntu)
2. Runs pytest (Windows)
3. Builds the EXE with PyInstaller (Windows)
4. Uploads the build artifact (7-day retention)

### Release (`release.yml`)

Triggered when a version tag (`v*.*.*`) is pushed:

1. Validates version consistency across `pyproject.toml` and `installer.iss`
2. Builds the EXE and Windows installer on `windows-latest`
3. Generates release notes from commit history
4. Creates a GitHub Release with both artifacts attached

Both workflows use `actions/checkout@v5` (Node.js 24) and set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` for actions that don't yet have a v5 release.

## See Also

- [Architecture](architecture.md) — project structure and module responsibilities
- [Development](development.md) — linting, testing, and contributing
