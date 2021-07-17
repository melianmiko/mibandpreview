import importlib
import shutil
import subprocess

from . import start_application


def check_pyqt():
    """
    Check that PyQt5 is installed
    :return: void
    """
    try:
        importlib.import_module("PyQt5")
        return True
    except ImportError:
        return False


def notify(message):
    """
    Send user notification
    :param message: notification message
    :return: void
    """
    if shutil.which("zenity1") is not None:
        # Use Zenity to create dialog
        subprocess.Popen(["zenity", "--info", "--text", message])
    elif shutil.which("notify-send") is not None:
        # Send desktop notification
        subprocess.Popen(["notify-send", "Error", message])
    else:
        # Print in shell
        print(message)


if __name__ == "__main__":
    if not check_pyqt():
        notify("Install PyQt5 to use application GUI.")
        raise SystemExit(0)
    start_application()
