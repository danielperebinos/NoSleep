import os
import threading
import sys
import socket
from pathlib import Path

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from loguru import logger

# Internal modules
import sleep_control
import autostart

# Single-instance lock port
INSTANCE_LOCK_PORT = 47200

# Global state
sleep_enabled = threading.Event()
sleep_enabled.set()  # sleep prevention is ON by default
auto = threading.Event()  # autostart state; set = enabled
instance_lock = None
wake_event = threading.Event()


def setup_logging():
    """Initializes logging to console and a local AppData file using pathlib."""
    logger.remove()

    local_appdata = os.environ.get("LOCALAPPDATA")
    app_data = (
        Path(local_appdata) if local_appdata else Path.home() / "AppData" / "Local"
    )
    logging_directory = app_data / "NoSleep" / "logs"

    # Console logging (only when running from source, not as a frozen GUI app)
    if not getattr(sys, "frozen", False) and sys.stderr:
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        )

    # Create directory structure; fall back to console-only logging on failure
    try:
        logging_directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.warning(
            f"Could not create log directory {logging_directory}: {e}. File logging disabled."
        )
        return

    logging_path = logging_directory / "app.log"

    # File logging with rotation and retention
    logger.add(
        str(logging_path),
        rotation="1 MB",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8",
    )

    logger.info(f"Logging initialized at: {logging_path}")


def check_single_instance():
    """Prevents multiple instances using a socket lock with SO_EXCLUSIVEADDRUSE."""
    global instance_lock
    try:
        instance_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        instance_lock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        instance_lock.bind(("127.0.0.1", INSTANCE_LOCK_PORT))
        logger.info(f"Instance lock acquired on port {INSTANCE_LOCK_PORT}")
    except socket.error:
        logger.warning("Another instance is already running. Exiting.")
        sys.exit(0)


MAX_WORKER_FAILURES = 5


def worker() -> None:
    """Background thread to keep the system awake."""
    logger.debug("Worker thread started")
    consecutive_failures = 0
    while True:
        if sleep_enabled.is_set():
            try:
                sleep_control.enable()
                logger.debug("Sleep prevention heartbeat sent")
                consecutive_failures = 0
            except Exception as e:
                consecutive_failures += 1
                logger.exception(f"Worker thread error: {e}")
                if consecutive_failures >= MAX_WORKER_FAILURES:
                    logger.critical(
                        f"sleep_control.enable() failed {consecutive_failures} times. Disabling."
                    )
                    sleep_enabled.clear()
                    consecutive_failures = 0
        # Clear BEFORE waiting so a set() that arrives between wait() returning
        # and clear() is not silently discarded on the next cycle.
        wake_event.clear()
        wake_event.wait(timeout=30)


def toggle_sleep(icon, item):
    if sleep_enabled.is_set():
        sleep_enabled.clear()
        logger.info("Sleep prevention toggled: DISABLED")
        try:
            sleep_control.disable()
        except (OSError, RuntimeError) as e:
            logger.error(f"sleep_control.disable() failed: {e}")
    else:
        sleep_enabled.set()
        logger.info("Sleep prevention toggled: ENABLED")

    wake_event.set()  # wake the worker so the change takes effect immediately
    icon.update_menu()


def toggle_autostart(icon, item) -> None:
    enabling = not auto.is_set()
    try:
        if enabling:
            autostart.enable()
            auto.set()
        else:
            autostart.disable()
            auto.clear()
        logger.info(f"Autostart {'ENABLED' if enabling else 'DISABLED'}")
    except (OSError, RuntimeError) as e:
        logger.error(f"Autostart toggle failed: {e}")
    icon.update_menu()


def on_exit(icon, item):
    global instance_lock
    logger.info("Application exiting...")
    # sleep_control.disable() is called in the finally block of main(); no need to call it here
    if instance_lock:
        instance_lock.close()
        instance_lock = None  # prevent double-close in finally block
    icon.stop()


def create_menu():
    is_frozen = getattr(sys, "frozen", False)
    menu_items = [
        MenuItem(
            "Prevent Sleep", toggle_sleep, checked=lambda item: sleep_enabled.is_set()
        ),
    ]
    # Autostart only makes sense for the installed EXE, not when running from source
    if is_frozen:
        menu_items.append(
            MenuItem("Autostart", toggle_autostart, checked=lambda item: auto.is_set())
        )
    menu_items += [Menu.SEPARATOR, MenuItem("Exit", on_exit)]
    return Menu(*menu_items)


def load_icon() -> Image.Image:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).parent

    icon_path = base / "icon.ico"
    if icon_path.exists():
        try:
            img = Image.open(icon_path)
            logger.info(f"Icon loaded from: {icon_path}")
            return img
        except OSError as e:
            logger.error(f"Failed to load icon: {e}")
    else:
        logger.warning(f"Icon not found at {icon_path}, using fallback")

    image = Image.new("RGB", (64, 64), color="blue")
    draw = ImageDraw.Draw(image)
    draw.ellipse([10, 10, 54, 54], fill="red", outline="darkred")
    draw.text((24, 26), "Z", fill="white")
    return image


def cleanup() -> None:
    try:
        sleep_control.disable()
    except (OSError, RuntimeError) as e:
        logger.error(f"sleep_control.disable() failed: {e}")
    if instance_lock:
        instance_lock.close()
    logger.info("Cleanup complete")


def main() -> None:
    setup_logging()
    logger.info("Starting NoSleep")
    check_single_instance()

    if autostart.is_enabled():
        auto.set()
    logger.info(f"Autostart: {'ENABLED' if auto.is_set() else 'DISABLED'}")

    threading.Thread(target=worker, daemon=True).start()

    try:
        Icon(
            "NoSleep", load_icon(), "NoSleep – Prevent System Sleep", menu=create_menu()
        ).run()
    except Exception as e:
        logger.critical(f"Main loop crashed: {e}")
        raise
    finally:
        cleanup()

    sys.exit(0)


if __name__ == "__main__":
    main()
