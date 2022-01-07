import os.path
import threading
import webbrowser
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QFileSystemWatcher, QLocale, QTranslator, pyqtSignal, QLibraryInfo

import mibandpreview
from . import ui_adapter, ui_frames, app_info, update_checker, preview_thread, pref_storage


# noinspection PyMethodMayBeStatic
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

        self.loader = mibandpreview.create()
        self.updater = update_checker.create(self)
        self.adapter = ui_adapter.create(self)

        self.watcher = QFileSystemWatcher()
        self.watcher.directoryChanged.connect(self.on_file_change)
        self.watcher.fileChanged.connect(self.on_file_change)

        self.previewThread = preview_thread.create(self)
        self.previewThread.render_completed.connect(self.set_preview_image)

        if os.path.isfile(app_info.SETTINGS_PATH):
            os.unlink(app_info.SETTINGS_PATH)

        if self.updater.should_check_updates():
            self.updater.start()

        if pref_storage.get("loader_data", None) is not None:
            self.loader.config_import(pref_storage.get("loader_data", None))
            self.adapter.load_config()

        if pref_storage.get("last_path", "") != "" and pref_storage.get("keep_last_path", True):
            self.bind_path(pref_storage.get("last_path", ""))

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
        if os.path.isfile(app_info.APP_ROOT+"/qt/app_"+locale_short+".qm"):
            translator.load(app_info.APP_ROOT+"/qt/app_"+locale_short+".qm")
            self.app.installTranslator(translator)

        # Update icon, title, current tab
        self.setWindowIcon(QIcon(app_info.APP_ROOT + "/res/mibandpreview-qt.png"))
        self.setWindowTitle(self.windowTitle() + " ({})".format(app_info.APP_VERSION))
        self.tabWidget.setCurrentIndex(0)

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

        self.bind_path(path)

    def bind_path(self, path):
        """
        Bind project path to application
        :param path: Target path
        :return: void
        """
        self.path = pref_storage.put("last_path", path)

        if path == "":
            self.set_preview_missing()
            return

        for a in self.watcher.directories():
            self.watcher.removePath(a)

        self.watcher.addPath(path)
        self.set_device("auto")
        self.loader.bind_path(path)

        self.adapter.setup_gif_ui()
        self.previewThread.start()

    def on_file_change(self):
        """
        On file change event handler
        :return:
        """
        try:
            self.loader.load_data()
            self.previewThread.start()
        except Exception as e:
            print("RELOAD ERROR: " + str(e))
            self.set_preview_error()

    def autoplay_init(self):
        """
        Initialize GIF autoplay
        :return:
        """
        self.adapter.setup_gif_ui()
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

    def set_angle(self, angle):
        pref_storage.put("preview_rotate", angle)

        self.rotate_0.setChecked(angle == 0)
        self.rotate_90.setChecked(angle == 90)
        self.rotate_270.setChecked(angle == 270)

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

    def set_angle_0(self):
        self.set_angle(0)
        self.previewThread.start()

    def set_angle_90(self):
        self.set_angle(90)
        self.previewThread.start()

    def set_angle_270(self):
        self.set_angle(270)
        self.previewThread.start()

    def wipe_config(self):
        pref_storage.wipe()
        self.app.exit(0)

    def open_site(self):
        webbrowser.open(app_info.LINK_WEBSITE)

    def open_github(self):
        webbrowser.open(app_info.LINK_GITHUB)

    def ui_widget_changed(self):
        if self.interactive:
            loader_data = self.adapter.read_ui()
            pref_storage.put("loader_data", loader_data)
            self.previewThread.start()

    def ui_gif_settings_changed(self):
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
        self.previewThread.start()
        self.autoplay_init()

    def set_preview_image(self, img, save_enabled):
        self.preview_host.setPixmap(img)
        self.action_save.setEnabled(save_enabled)
