### NoSleep

run command to build NoSleep executable:
```bash
pyinstaller --onefile --noconsole --icon=icon.ico --name NoSleep main.py
```

```bash
pyinstaller --noconsole --onefile --add-data "icon.ico;." --icon=icon.ico main.py
```