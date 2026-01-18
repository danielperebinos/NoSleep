import os
import threading
import time
import sys
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sleep_control
import autostart

enabled = True
auto = False


def worker():
    while True:
        if enabled:
            sleep_control.enable()
        time.sleep(30)


def toggle_sleep(icon, item):
    global enabled
    enabled = not enabled
    if not enabled:
        sleep_control.disable()
    icon.update_menu()


def toggle_autostart(icon, item):
    global auto
    auto = not auto
    if auto:
        autostart.enable()
    else:
        autostart.disable()
    icon.update_menu()


def on_exit(icon, item):
    sleep_control.disable()
    icon.stop()
    sys.exit(0)


def create_menu():
    return Menu(
        MenuItem(
            "Защита от сна",
            toggle_sleep,
            checked=lambda item: enabled
        ),
        MenuItem(
            "Автозапуск",
            toggle_autostart,
            checked=lambda item: auto
        ),
        Menu.SEPARATOR,
        MenuItem("Выход", on_exit)
    )


def load_icon():
    if getattr(sys, 'frozen', False):
        # Если это exe-файл
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    possible_paths = [
        os.path.join(base_path, "icon.ico"),
        os.path.join(base_path, "..", "icon.ico"),
        os.path.join(os.getcwd(), "icon.ico"),
        os.path.join(os.path.dirname(sys.executable), "icon.ico"),
    ]

    for icon_path in possible_paths:
        try:
            if os.path.exists(icon_path):
                print(f"Icon found at: {icon_path}")
                return Image.open(icon_path)
        except FileNotFoundError:
            continue

    # Если иконка не найдена, создаем простую
    print("Icon not found, creating default...")  # Для отладки
    image = Image.new('RGB', (64, 64), color='blue')
    draw = ImageDraw.Draw(image)
    draw.ellipse([10, 10, 54, 54], fill='red', outline='darkred')
    draw.text((24, 26), "Z", fill='white')
    return image


def main():
    threading.Thread(target=worker, daemon=True).start()

    icon = Icon(
        "NoSleep",
        load_icon(),
        "NoSleep – Prevent Sleep",
        menu=create_menu()
    )
    icon.run()


if __name__ == "__main__":
    main()
