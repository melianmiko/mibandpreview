import sys

from PyQt5.QtWidgets import QApplication

from . import update_checker
from .update_checker import UpdateCheckerUI
from .config_manager import ConfigManager
from .preview_thread import PreviewThread
from .main import MiBandPreviewApp


def start_application():
    app = QApplication(sys.argv)
    window = MiBandPreviewApp(app)
    window.show()
    app.exec_()
