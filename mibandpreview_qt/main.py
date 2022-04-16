import base64
import logging
import os.path
import threading
import webbrowser
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QFileSystemWatcher, QLocale, QTranslator, pyqtSignal, QLibraryInfo

import mibandpreview
from mibandpreview_qt import ui_adapter, ui_frames, app_info, update_checker, preview_thread, pref_storage

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("PIL.PngImagePlugin").disabled = True
log = logging.getLogger("PreviewQT")


class MiBandPreviewApp(QMainWindow, ui_frames.Ui_MainWindow):
    frames = [0, 0, 0, 0, 0]
    player_toggle = [False, False, False, False, False]
    player_state = [False, False, False, False, False]
    player_started = False
    interactive = True
    save_allowed = False
    angle = 0
    path = ""

    rebuild_required = pyqtSignal()

    # noinspection PyUnresolvedReferences
    def __init__(self, context_app):
        """
        Default constructor
        :param context_app: Qt Application object
        """
        super().__init__()
        self.app = context_app
        self.init_qt()

        # Create all submodules
        self.loader = mibandpreview.create()
        self.updater = update_checker.create(self)
        self.adapter = ui_adapter.create(self)

        # Setup FS watcher
        self.watcher = QFileSystemWatcher()
        self.watcher.directoryChanged.connect(self.on_file_change)
        self.watcher.fileChanged.connect(self.on_file_change)

        # Spawn preview thread
        self.previewThread = preview_thread.create(self)
        self.previewThread.render_completed.connect(self.set_preview_image)

        # Load settings
        self.rotate_settings.setCurrentIndex(pref_storage.get("preview_rotate", 0))
        self.loader.config_import(pref_storage.get("loader_data", {}))

        # Loader config -> GUI
        self.adapter.load_config()

        # Start update checker, if enabled
        if self.updater.should_check_updates():
            self.updater.start()

        # Restore last path, if saved
        if pref_storage.get("last_project_file", "") != "" and pref_storage.get("keep_last_path", True):
            self.bind_json_path(pref_storage.get("last_project_file", ""))

    def init_qt(self):
        """
        Load QT translation file, if available
        :return: void
        """
        super().setupUi(self)

        locale = QLocale.system().name()
        locale_short = locale[0:2]

        # Qt Translator
        translator = QTranslator(self.app)
        translator.load("qtbase_" + locale,
                        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        self.app.installTranslator(translator)

        # App translator
        translator = QTranslator(self.app)
        if os.path.isfile(app_info.APP_ROOT + "/qt/app_"+locale_short+".qm"):
            translator.load(app_info.APP_ROOT + "/qt/app_"+locale_short+".qm")
            self.app.installTranslator(translator)
        self.retranslateUi(self)

        # Update icon, title, current tab
        self.setWindowIcon(QIcon(app_info.APP_ROOT + "/res/mibandpreview-qt.png"))
        self.update_window_title()
        self.tabWidget.setCurrentIndex(0)

        # Restore geometry
        geometry = base64.b64decode(pref_storage.get("main_geometry", "").encode("ascii"))
        # state = base64.b64decode(pref_storage.get("main_state", "").encode("ascii"))
        self.restoreGeometry(geometry)
        # self.restoreState(state)

    def update_window_title(self):
        title = "Mi Band Preview | " + app_info.APP_VERSION
        if self.path != "":
            title = os.path.basename(self.path) + " | " + title
        self.setWindowTitle(title)

    def save_as_png(self):
        """
        Save current GUI image to file
        :return: void
        """
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, "Save image",
                                              str(Path.home()), "Image (*.png)", options=options)

        if path == "":
            return

        if not path.endswith(".png"):
            path += ".png"

        data = self.loader.render_with_animation_frame(self.frames)
        data[0].save(path)

    def open_project_json(self):
        """
        Show project open dialog (JSON file select)
        :return: void
        """
        files, _ = QFileDialog.getOpenFileNames(None, "Select watchface JSON file",
                                                str(Path.home()))

        if len(files) > 0:
            path = files[0]
            if not path.endswith(".json") or os.path.isdir(path):
                log.debug("Invalid select, ignored")
                return
            self.bind_json_path(path)

    def open_project(self):
        """
        Show project open dialog
        :return: void
        """
        path = QFileDialog.getExistingDirectory(None,
                                                "Select unpacked (!) watchface folder",
                                                str(Path.home()), QFileDialog.ShowDirsOnly)

        if path == "":
            return

        json_path = ""
        for f in os.listdir(path):
            if os.path.splitext(path + "/" + f)[1] == ".json":
                json_path = path + "/" + f
                break

        self.bind_json_path(json_path)

    def bind_json_path(self, json_path):
        """
        Bind project JSOn file path to application
        :param json_path: Target JSON file path
        :return: void
        """
        log.debug("Change project path to " + json_path)
        self.path = pref_storage.put("last_project_file", json_path)
        self.update_window_title()

        for a in self.watcher.directories():
            self.watcher.removePath(a)

        dir_path = os.path.dirname(json_path)
        if os.path.isdir(dir_path) and not dir_path == "":
            self.watcher.addPath(dir_path)

        self.set_device("auto")
        if not self.previewThread.bind_json(json_path):
            self.path = ""
            return

        self.setup_gif_ui()
        self.previewThread.start()

    def on_file_change(self):
        """
        On file change event handler
        :return:
        """
        self.loader.load_data()
        self.previewThread.start()

    def autoplay_init(self):
        """
        Initialize GIF autoplay
        :return:
        """
        self.setup_gif_ui()
        if self.player_started and True in self.player_toggle:
            # Already started, ignoring
            return

        if True in self.player_toggle:
            # Start player
            self.player_started = True
            self.autoplay_handler()
        else:
            self.player_started = False

    # noinspection PyUnusedLocal
    def autoplay_handler(self, a0=0):
        """
        Change GIF frame handler
        :return: void
        """
        if not self.player_started:
            return

        for a in range(0, 5):
            if self.player_toggle[a]:
                if self.player_state[a]:
                    self.frames[a] = 0
                else:
                    self.frames[a] += 1

        self.previewThread.start()
        threading.Timer(0.05, self.autoplay_handler, args=(self,)).start()

    def set_device(self, device):
        self.loader.set_property("device", device)

        # self.action_save.setEnabled(self.preview_ready)
        self.target_mb4.setChecked(device == "miband4")
        self.target_mb5.setChecked(device == "miband5")
        self.target_mb6.setChecked(device == "miband6")

    # QT Events
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        """
        Window resized event handler
        :param a0: some argument?
        :return: void
        """
        self.previewThread.start()
        return QMainWindow.resizeEvent(self, a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        Window close event handler
        :param a0: some argument
        :return: void
        """
        self.player_started = False
        pref_storage.save()

        # Save geometry
        geometry = base64.b64encode(self.saveGeometry()).decode("ascii")
        # state = base64.b64encode(self.saveState()).decode("ascii")
        pref_storage.put("main_geometry", geometry)
        # pref_storage.put("main_state", state)
        pref_storage.save()

        return QMainWindow.closeEvent(self, a0)

    def set_target_mb4(self):
        self.set_device("miband4")
        self.previewThread.start()

    def set_target_mb5(self):
        self.set_device("miband5")
        self.previewThread.start()

    def set_target_mb6(self):
        self.set_device("miband6")
        self.previewThread.start()

    def set_rotate_option(self, val):
        pref_storage.put("preview_rotate", val)
        self.rotate_settings.setCurrentIndex(val)
        self.previewThread.start()

    def wipe_config(self):
        pref_storage.wipe()
        self.app.exit(0)

    @staticmethod
    def open_site():
        webbrowser.open(app_info.LINK_WEBSITE)

    @staticmethod
    def open_github():
        webbrowser.open(app_info.LINK_GITHUB)

    def ui_widget_changed(self):
        if self.interactive:
            loader_data = self.adapter.read_ui()
            pref_storage.put("loader_data", loader_data)
            self.previewThread.start()

    def ui_gif_settings_changed(self):
        self.read_gif_ui()
        self.previewThread.start()
        self.autoplay_init()

    def set_preview_image(self, img, save_enabled: bool):
        self.preview_host.setPixmap(img)
        self.action_save.setEnabled(save_enabled)

    def read_gif_ui(self):
        self.frames = [
            self.anim_frame_0.value(),
            self.anim_frame_1.value(),
            self.anim_frame_2.value(),
            self.anim_frame_3.value(),
            self.anim_frame_4.value()
        ]
        self.player_toggle = [
            self.anim_play_0.isChecked(),
            self.anim_play_1.isChecked(),
            self.anim_play_2.isChecked(),
            self.anim_play_3.isChecked(),
            self.anim_play_4.isChecked()
        ]

    def setup_gif_ui(self):
        c = self.loader.get_animations_count()
        t = self.player_toggle

        self.anim_frame_0.setEnabled(c > 0 and not t[0])
        self.anim_frame_1.setEnabled(c > 1 and not t[1])
        self.anim_frame_2.setEnabled(c > 2 and not t[2])
        self.anim_frame_3.setEnabled(c > 3 and not t[3])
        self.anim_frame_4.setEnabled(c > 4 and not t[4])

        self.anim_play_0.setEnabled(c > 0)
        self.anim_play_1.setEnabled(c > 1)
        self.anim_play_2.setEnabled(c > 2)
        self.anim_play_3.setEnabled(c > 3)
        self.anim_play_4.setEnabled(c > 4)

    def setup_updater(self):
        self.updater.reconfigure()
