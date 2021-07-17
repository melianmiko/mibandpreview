"""This module contains simple Qt5 GUI for mibandpreview app"""
import sys
from PyQt5.QtWidgets import QApplication
from .main import MiBandPreviewApp


def start_application():
    """
    Start Qt application
    :return: void
    """
    app = QApplication(sys.argv)
    window = MiBandPreviewApp(app)
    window.show()
    app.exec_()
