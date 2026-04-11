[← Building](building.md) · [Back to README](../README.md)

# Development

## Lint & Format

```bash
uv run ruff check .
uv run ruff format .
```

Ruff is configured as the sole linter/formatter. CI runs `ruff format --check` and `ruff check` on every push.

## Testing

```bash
uv run pytest tests/ -v --tb=short
```

Tests run on Windows in CI (`windows-latest`). The test suite uses `pytest-mock` to mock Windows-specific APIs (`ctypes`, `winreg`).

| Test File | Covers |
|-----------|--------|
| `test_main.py` | Worker logic, toggle functions, lifecycle |
| `test_sleep_control.py` | SetThreadExecutionState wrapper |
| `test_autostart.py` | Registry key management |

## Contributing

Contributions are welcome!

1. Fork the project
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m "Add AmazingFeature"`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## See Also

- [Getting Started](getting-started.md) — setup and running
- [Building](building.md) — packaging for distribution
