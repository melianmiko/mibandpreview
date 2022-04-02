import logging

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QMessageBox

from . import app_info, pref_storage, mmk_updater

DEFAULT_UPDATE_CHECKER_STATE = True

# noinspection HttpUrlsUsage
release_url = "http://st.melianmiko.ru/mibandpreview/release.json"
log = logging.getLogger("UpdateChecker")


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
        self.tool = mmk_updater.UpdaterTool(release_url, app_info.VERSION)

    def start(self):
        """
        Start update checker
        :return: void
        """
        log.info("Checking for new version...")
        self.tool.start()

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

        log.info("New update checker state: " + str(answer))
        pref_storage.put("updater_enabled", answer)

        return answer
