"""This module contains simple Qt5 GUI for mibandpreview app"""


def start_application():
    """
    Start Qt application
    :return: void
    """
    import sys
    from PyQt5.QtWidgets import QApplication
    from .main import MiBandPreviewApp

    app = QApplication(sys.argv)
    window = MiBandPreviewApp(app)
    window.show()
    app.exec_()
