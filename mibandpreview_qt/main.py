import json
import os.path
import platform
import threading
import urllib.request
import webbrowser
from PIL import Image
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QFileSystemWatcher, QLocale, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

import mibandpreview
from .MainWindow import Ui_MainWindow
from . import UiHandler, app_info, update_checker


class MiBandPreviewApp(QtWidgets.QMainWindow, Ui_MainWindow):
    path = ""
    frames = [0, 0, 0, 0, 0]
    player_toggle = [False, False, False, False, False]
    player_state = [False, False, False, False, False]
    player_started = False
    update_checker_enabled = True

    def load_translation(self):
        locale = QLocale.system().name()[0:2]
        translator = QTranslator(self.app)
        if os.path.isfile(app_info.APP_ROOT+"/qt/app_"+locale+".qm"):
            print("Loading translation "+str(locale))
            translator.load(app_info.APP_ROOT+"/qt/app_"+locale+".qm")
            self.app.installTranslator(translator)

    def __init__(self, context_app):
        super().__init__()

        self.app = context_app                              # type: QtWidgets.QApplication
        self.load_translation()
        self.setupUi(self)

        self.loader = mibandpreview.MiBandPreview()         # type: mibandpreview.MiBandPreview
        self.watcher = QFileSystemWatcher()                 # type: QFileSystemWatcher
        self.handler = UiHandler.create(self)               # type: UiHandler

        self.setWindowIcon(QIcon(app_info.APP_ROOT + "/res/mibandpreview-qt.png"))
        self.tabWidget.setCurrentIndex(0)

        self.update_thread = update_checker.UpdateChecker()
        self.bind_signals()

        self.handler.set_user_settings()
        self.handler.get_user_settings()
        self.handler.set_no_preview()
        self.load_data()

        if self.should_check_updates():
            self.update_thread.start()

    def on_update_available(self, url, version):
        qm = QMessageBox()
        qm.setModal(True)

        locale = QLocale.system().name()[0:2]
        message = "New version available {}. Download now?"
        if locale == "ru":
            message = "Доступна новая версия {}. Скачать?"

        r = qm.question(self,
                        'Update checker',
                        message.replace("{}", version),
                        qm.Yes | qm.No | qm.Ignore)

        if r == qm.Ignore:
            self.cfg_updater()

        if r == qm.Yes:
            webbrowser.open(url)

    # noinspection PyUnresolvedReferences
    def bind_signals(self):
        self.watcher.directoryChanged.connect(self.on_file_change)
        self.watcher.fileChanged.connect(self.on_file_change)
        self.update_thread.has_updates.connect(self.on_update_available)

    def cfg_updater(self):
        self.update_checker_enabled = None
        self.should_check_updates()

    def should_check_updates(self):
        if self.update_checker_enabled is not None:
            return self.update_checker_enabled

        qm = QMessageBox()
        qm.setModal(True)

        locale = QLocale.system().name()[0:2]
        if locale == "ru":
            message = "Проверять наличие обновлений при запуске программы?"
        else:
            message = "Check for updates on app start?"

        answer = qm.question(self, "Update checker", message, qm.Yes | qm.No) == qm.Yes
        print("New update checker state: " + str(answer))
        self.update_checker_enabled = answer

        return answer

    def save_image(self, path):
        img, state = self.loader.render_with_animation_frame(self.frames)
        img.save(path)

    def rebuild(self):
        if self.path == "" or not os.path.isdir(self.path):
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
        with open(app_info.SETTINGS_PATH, "w") as f:
            f.write("{}")
        self.app.exit(0)

    def on_exit(self):
        self.player_started = False
        self.save_data()

    def load_data(self):
        if not os.path.isfile(app_info.SETTINGS_PATH):
            return

        try:
            with open(app_info.SETTINGS_PATH, "r") as f:
                data = json.loads(f.read())

                if data["version"] != app_info.SETTINGS_VER:
                    print("Ignoring settings file, version mismatch")
                    return

                self.loader.config_import(data["preview_data"])
                self.bind_path(data["last_path"])
                self.handler.set_user_settings()
                self.update_checker_enabled = data["update_checker_enabled"]

        except Exception as e:
            print(e)
            print("Can't load settings")

    def save_data(self):
        try:

            settings = {
                "preview_data": self.loader.config_export(),
                "last_path": self.path,
                "version": app_info.SETTINGS_VER,
                "update_checker_enabled": self.update_checker_enabled
            }

            with open(app_info.SETTINGS_PATH, "w") as f:
                f.write(json.dumps(settings))
            print("Settings saved to " + app_info.SETTINGS_PATH)

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

    def autoplay_handler(self):
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
