import os
import threading
import time
import sys
import socket
from pathlib import Path

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from loguru import logger

# Internal modules
import sleep_control
import autostart

# Global state
enabled = True
auto = False
instance_lock = None


def setup_logging():
    """Initializes logging to console and a local AppData file using pathlib."""
    logger.remove()

    app_data = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    logging_directory = app_data / "NoSleep" / "logs"

    # Create directory structure
    logging_directory.mkdir(parents=True, exist_ok=True)
    logging_path = logging_directory / "app.log"

    # Console logging (only if terminal is available)
    if sys.stderr:
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        )

    # File logging with rotation and retention
    logger.add(
        str(logging_path),
        rotation="1 MB",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8",
    )

    logger.info(f"Logging initialized at: {logging_path}")


def check_single_instance(port=47200):
    """Prevents multiple instances using a socket lock."""
    global instance_lock
    try:
        instance_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        instance_lock.bind(("127.0.0.1", port))
        logger.info(f"Instance lock acquired on port {port}")
    except socket.error:
        logger.warning("Another instance is already running. Exiting.")
        sys.exit(0)


def worker():
    """Background thread to keep the system awake."""
    logger.debug("Worker thread started")
    while True:
        if enabled:
            sleep_control.enable()
            logger.debug("Sleep prevention heartbeat sent")
        time.sleep(30)


def toggle_sleep(icon, item):
    global enabled
    enabled = not enabled
    state = "ENABLED" if enabled else "DISABLED"
    logger.info(f"Sleep prevention toggled: {state}")

    if not enabled:
        sleep_control.disable()
    icon.update_menu()


def toggle_autostart(icon, item):
    global auto
    auto = not auto
    state = "ENABLED" if auto else "DISABLED"
    logger.info(f"Autostart toggled: {state}")

    if auto:
        autostart.enable()
    else:
        autostart.disable()
    icon.update_menu()


def on_exit(icon, item):
    logger.info("Application exiting...")
    sleep_control.disable()
    icon.stop()
    sys.exit(0)


def create_menu():
    return Menu(
        MenuItem("Prevent Sleep", toggle_sleep, checked=lambda item: enabled),
        MenuItem("Autostart", toggle_autostart, checked=lambda item: auto),
        Menu.SEPARATOR,
        MenuItem("Exit", on_exit),
    )


def load_icon():
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    possible_paths = [
        os.path.join(base_path, "icon.ico"),
        os.path.join(os.getcwd(), "icon.ico"),
    ]

    for icon_path in possible_paths:
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                logger.info(f"Icon loaded from: {icon_path}")
                return img
        except Exception as e:
            logger.error(f"Failed to load icon at {icon_path}: {e}")
            continue

    logger.warning("No icon file found, creating fallback visual")
    image = Image.new("RGB", (64, 64), color="blue")
    draw = ImageDraw.Draw(image)
    draw.ellipse([10, 10, 54, 54], fill="red", outline="darkred")
    draw.text((24, 26), "Z", fill="white")
    return image


def main():
    setup_logging()
    logger.info("Starting NoSleep Application")

    check_single_instance()

    # Daemon thread ensures the thread exits when the main process does
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    try:
        icon = Icon(
            "NoSleep", load_icon(), "NoSleep – Prevent System Sleep", menu=create_menu()
        )
        icon.run()
    except Exception as e:
        logger.critical(f"Main loop crashed: {e}")


if __name__ == "__main__":
    main()
