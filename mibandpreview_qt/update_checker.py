import json
import platform
import urllib.request
import webbrowser

from PyQt5.QtCore import QThread, pyqtSignal, QLocale
from PyQt5.QtWidgets import QMessageBox

from . import app_info


def create(app):
    return UpdateCheckerUI(app)


class UpdateCheckerUI:
    """
    This class contains all parts of update checker UI.
    """

    def __init__(self, app):
        """
        Initialize this app
        :param app: Main application window
        """
        self.app = app
        self.update_checker_enabled = True
        self.thread = UpdateCheckerThread(self.app)

        # noinspection PyUnresolvedReferences
        self.thread.has_updates.connect(self.on_update_available)

        # Bind QT actions
        self.app.action_configure_updater.triggered.connect(self.reconfigure)

    def start(self):
        """
        Start update checker
        :return: void
        """
        print("Checking for new version...")
        self.thread.start()

    def on_update_available(self, url, version):
        """
        On update available handler
        :param url: download URL, or homepage url
        :param version: version name
        :return: void
        """
        qm = QMessageBox()
        qm.setModal(True)

        # Get localized message
        # TODO: Use locale module
        locale = QLocale.system().name()[0:2]
        message = "New version available {}. Download now?"
        if locale == "ru":
            message = "Доступна новая версия {}. Скачать?"

        # Spawn question
        r = qm.question(self.app,
                        'Update checker',
                        message.replace("{}", version),
                        qm.Yes | qm.No | qm.Ignore)

        # If user select "Ignore" button, show settings dialog
        if r == qm.Ignore:
            self.reconfigure()

        # If user accepted update, open browser
        if r == qm.Yes:
            webbrowser.open(url)

    def reconfigure(self):
        """
        Clear current settings and show configure dialog
        :return: void
        """
        self.update_checker_enabled = None
        self.should_check_updates()

    def should_check_updates(self):
        """
        Check, is updater enabled. If prop missing, ask user.
        :return: True, if enabled
        """
        if self.update_checker_enabled is not None:
            return self.update_checker_enabled

        qm = QMessageBox()
        qm.setModal(True)

        locale = QLocale.system().name()[0:2]
        if locale == "ru":
            message = "Проверять наличие обновлений при запуске программы?"
        else:
            message = "Check for updates on app start?"

        answer = qm.question(self.app,
                             "Update checker",
                             message,
                             qm.Yes | qm.No)

        answer = answer == qm.Yes

        print("New update checker state: " + str(answer))
        self.update_checker_enabled = answer

        return answer


def get_exe_url(res):
    """
    Get windows installer URL from github response
    :param res: GitHub releases API response
    :return: URL
    """
    url = app_info.LINK_WEBSITE

    for a in res["assets"]:
        if a["name"].endswith(".exe"):
            url = a["browser_download_url"]

    return url


class UpdateCheckerThread(QThread):
    """
    Update checker thread
    """
    has_updates = pyqtSignal(str, str)

    # noinspection PyBroadException
    def run(self):
        """
        Check updates via GitHub API
        :return: void
        """
        try:
            res = urllib.request.urlopen(
                "https://api.github.com/repos/melianmiko/mibandpreview/releases",
                timeout=3
            )
        except Exception:
            print("Update check failed", flush=True)
            return

        res = json.loads(res.read())[0]

        if not res["tag_name"] == app_info.APP_VERSION:
            print("New version: " + app_info.APP_VERSION + " != " + res["tag_name"])
            url = app_info.LINK_WEBSITE

            if platform.system() == "Windows":
                url = get_exe_url(res)

            print("Download url: " + url)

            # noinspection PyUnresolvedReferences
            self.has_updates.emit(url, res["tag_name"])
        else:
            print("Already latest: " + app_info.APP_VERSION)
