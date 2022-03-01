import json
import platform
import urllib.request
import webbrowser

from PyQt5.QtCore import QThread, pyqtSignal, QLocale
from PyQt5.QtWidgets import QMessageBox

from . import app_info, pref_storage


DEFAULT_UPDATE_CHECKER_STATE = True
# noinspection HttpUrlsUsage
release_url = "http://st.melianmiko.ru/mibandpreview/release.json"


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
        pref_storage.put("updater_enabled", None)
        self.should_check_updates()

    def should_check_updates(self):
        """
        Check, is updater enabled. If prop missing, ask user.
        :return: True, if enabled
        """
        if pref_storage.get("updater_enabled", DEFAULT_UPDATE_CHECKER_STATE) is not None:
            return pref_storage.get("updater_enabled", DEFAULT_UPDATE_CHECKER_STATE)

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
        pref_storage.put("updater_enabled", answer)

        return answer


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
            res = urllib.request.urlopen(release_url, timeout=3)
        except Exception:
            print("Update check failed", flush=True)
            return

        res = json.loads(res.read())

        if res["version"] == app_info.VERSION:
            print("No updates")
            return

        url = app_info.LINK_WEBSITE
        if platform.system() == "Windows" and "windows" in res:
            url = res["windows"][0]["url"]

        print("New version: " + app_info.VERSION + " != " + res["version"])
        print("Download url: " + url)

        # noinspection PyUnresolvedReferences
        self.has_updates.emit(url, res["version"])
