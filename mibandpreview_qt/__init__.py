import json
import os.path
import platform
import sys
import threading
import urllib.request
from pathlib import Path
from PIL import Image
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QFileSystemWatcher, QLocale, QTranslator
from PyQt5.QtGui import QIcon

import app_info
import mibandpreview
import mibandpreview_qt.use_certifi # Fix SSL issue on Windows
from mibandpreview_qt.MainWindow import Ui_MainWindow
from mibandpreview_qt import UiHandler

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = str(Path.home())+"/.mi_band_preview.json"
SETTINGS_VER = 3
APP_VERSION = "0.7.2"


class MiBandPreviewApp(QtWidgets.QMainWindow, Ui_MainWindow):
    path = ""
    frames = [0, 0, 0, 0, 0]
    player_toggle = [False, False, False, False, False]
    player_state = [False, False, False, False, False]
    player_started = False

    def load_translation(self):
        locale = QLocale.system().name()[0:2]
        translator = QTranslator(self.app)
        if os.path.isfile(APP_ROOT+"/qt/app_"+locale+".qm"):
            print("Loading translation "+str(locale))
            translator.load(APP_ROOT+"/qt/app_"+locale+".qm")
            self.app.installTranslator(translator)

    def __init__(self, context_app):
        super().__init__()

        self.app = context_app                              # type: QtWidgets.QApplication
        self.load_translation()
        self.setupUi(self)

        self.loader = mibandpreview.create()                # type: mibandpreview.MiBandPreview
        self.watcher = QFileSystemWatcher()                 # type: QFileSystemWatcher
        self.handler = UiHandler.create(self)               # type: UiHandler

        self.setWindowIcon(QIcon(APP_ROOT+"/res/icon.png"))
        self.tabWidget.setCurrentIndex(0)
        self.watcher.directoryChanged.connect(self.on_file_change)
        self.watcher.fileChanged.connect(self.on_file_change)

        self.handler.set_user_settings()
        self.handler.get_user_settings()
        self.handler.set_no_preview()
        self.load_data()

        self.check_updates()

    def save_image(self, path):
        img, state = self.loader.render_with_animation_frame(self.frames)
        img.save(path)

    def check_updates(self, *args):
        print(platform.system())
        try:
            if platform.system() == "Windows":
                res = urllib.request.urlopen(
                    "https://gitlab.com/api/v4/projects/melianmiko%2Fmibandpreview/releases",
                    timeout=3
                    )
                res = json.loads(res.read())[0]
                if not res["tag_name"] == APP_VERSION:
                    print("New version: "+APP_VERSION+" != "+res["tag_name"])
                    url = app_info.LINK_WEBSITE
                    for a in res["assets"]["links"]:
                        if a["name"] == "windows_installer":
                            url = a["url"]
                            print("Download url: "+url)
                    self.handler.show_update_dialog(url)
        except Exception as e:
            print(e)

    def rebuild(self):
        if self.path == "":
            self.handler.set_no_preview()
            return

        try:
            img, state = self.loader.render_with_animation_frame(self.frames)
            sf = self.get_scale_factor(img.size)
            img = img.resize((round(img.size[0] * sf), round(img.size[1] * sf)), resample=Image.BOX)

            self.player_state = state
            self.handler.set_preview(img)
        except Exception as e:
            print("RENDER ERROR: "+str(e))
            self.handler.set_error_preview()

    def exit(self):
        self.on_exit()
        self.app.exit(0)

    def wipe(self):
        with open(SETTINGS_PATH, "w") as f:
            f.write("{}")
        self.app.exit(0)

    def on_exit(self):
        self.player_started = False
        self.save_data()

    def load_data(self):
        if not os.path.isfile(SETTINGS_PATH):
            return

        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.loads(f.read())

                if data["version"] != SETTINGS_VER:
                    print("Ignoring settings file, version mismatch")
                    return

                self.loader.config_import(data["preview_data"])
                self.bind_path(data["last_path"])
                self.handler.set_user_settings()

        except Exception as e:
            print(e)
            print("Can't load settings")

    def save_data(self):
        try:

            settings = {
                "preview_data": self.loader.config_export(),
                "last_path": self.path,
                "version": SETTINGS_VER
            }

            with open(SETTINGS_PATH, "w") as f:
                f.write(json.dumps(settings))
            print("Settings saved to "+SETTINGS_PATH)

        except Exception as e:
            print(e)
            print("Can't save settings")

    def bind_path(self, path):
        if path == "":
            self.handler.set_no_preview()
            return

        for a in self.watcher.directories():
            self.watcher.removePath(a)

        self.path = path
        self.watcher.addPath(path)
        self.loader.set_property("device", "auto")
        self.loader.bind_path(path)
        print("Using path: "+path)

        self.handler.setup_gif_ui()

        self.rebuild()

    def on_file_change(self):
        self.loader.load_data()
        self.rebuild()

    def on_ui_change(self):
        self.handler.get_user_settings()
        self.rebuild()

    def autoplay_init(self):
        self.handler.setup_gif_ui()
        if self.player_started and True in self.player_toggle:
            # Already started, ignoring
            return

        if True in self.player_toggle:
            # Start player
            self.player_started = True
            self.autoplay_handler()
        else:
            self.player_started = False

    def autoplay_handler(self, *args):
        if not self.player_started:
            return

        for a in range(0, 5):
            if self.player_toggle[a]:
                if self.player_state[a]:
                    self.frames[a] = 0
                else:
                    self.frames[a] += 1

        self.rebuild()
        threading.Timer(0.05, self.autoplay_handler, args=(self,)).start()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.rebuild()
        return QtWidgets.QMainWindow.resizeEvent(self, a0)

    def get_scale_factor(self, size):
        w = self.width() / 3
        h = self.height() - 10
        ratio = min(w / size[0], h / size[1])
        ratio = round(max(1, ratio), 1)
        return ratio

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.on_exit()
        return QtWidgets.QMainWindow.closeEvent(self, a0)


def start():
    app = QtWidgets.QApplication(sys.argv)
    window = MiBandPreviewApp(app)
    window.show()
    app.exec_()
