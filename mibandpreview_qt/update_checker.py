import json
import platform
import urllib.request

from PyQt5.QtCore import QThread, pyqtSignal

from . import app_info


class UpdateChecker(QThread):
    has_updates = pyqtSignal(str, str)

    def get_exe_url(self, res):
        url = app_info.LINK_WEBSITE

        for a in res["assets"]:
            if a["name"].endswith(".exe"):
                url = a["browser_download_url"]

        return url

    def run(self):
        res = urllib.request.urlopen(
            "https://api.github.com/repos/melianmiko/mibandpreview/releases",
            timeout=3
        )

        res = json.loads(res.read())[0]

        if not res["tag_name"] == app_info.APP_VERSION:
            print("New version: " + app_info.APP_VERSION + " != " + res["tag_name"])
            url = app_info.LINK_WEBSITE

            if platform.system() == "Windows":
                url = self.get_exe_url(res)

            print("Download url: " + url)

            # noinspection PyUnresolvedReferences
            self.has_updates.emit(url, res["tag_name"])
