import sys

from PyQt5.QtWidgets import QApplication
from .main import MiBandPreviewApp


def start_application():
    app = QApplication(sys.argv)
    window = MiBandPreviewApp(app)
    window.show()
    app.exec_()
