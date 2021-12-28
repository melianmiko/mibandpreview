import os.path
import threading
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QFileSystemWatcher, QLocale, QTranslator, pyqtSignal, QLibraryInfo

import mibandpreview
from . import ui_adapter, app_info, update_checker, config_manager, preview_thread
from .main_slots import Ui_MainWindowWithSlots
from .MainWindow import Ui_MainWindow


# noinspection PyMethodMayBeStatic
class MiBandPreviewApp(QMainWindow, Ui_MainWindow, Ui_MainWindowWithSlots):
    player_state = [False, False, False, False, False]
    player_started = False
    interactive = True
    save_allowed = False
    angle = 0
    path = ""

    rebuild_required = pyqtSignal()

    def __init__(self, context_app):
        """
        Default constructor
        :param context_app: Qt Application object
        """
        super().__init__()
        self.app = context_app

        self.load_translation()
        self.setupUi(self)

        self.setWindowIcon(QIcon(app_info.APP_ROOT + "/res/mibandpreview-qt.png"))
        self.setWindowTitle(self.windowTitle() + " ({})".format(app_info.APP_VERSION))
        self.tabWidget.setCurrentIndex(0)

        self.loader = mibandpreview.MiBandPreview()         # type: mibandpreview.MiBandPreview
        self.watcher = QFileSystemWatcher()                 # type: QFileSystemWatcher

        self.updater = update_checker.create(self)
        self.config = config_manager.create(self)
        self.generator = preview_thread.create(self)

        self.adapter = ui_adapter.create(self)

        self.bind_signals()
        self.set_angle(0)

        self.set_preview_missing()
        self.config.load()

        if self.updater.should_check_updates():
            self.updater.start()

    def load_translation(self):
        """
        Load QT translation file, if available
        :return: void
        """
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

    # noinspection PyUnresolvedReferences
    def bind_signals(self):
        """
        Bind signal listeners
        :return: void
        """
        self.watcher.directoryChanged.connect(self.on_file_change)
        self.watcher.fileChanged.connect(self.on_file_change)
        self.generator.image_ready.connect(self.set_preview_image)
        self.generator.image_missing.connect(self.set_preview_missing)
        self.generator.image_failed.connect(self.set_preview_error)

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
        self.path = path

        if path == "":
            self.set_preview_missing()
            return

        for a in self.watcher.directories():
            self.watcher.removePath(a)

        self.watcher.addPath(path)
        self.set_device("auto")
        self.loader.bind_path(path)

        self.adapter.setup_gif_ui()
        self.rebuild()

    def on_file_change(self):
        """
        On file change event handler
        :return:
        """
        try:
            self.loader.load_data()
            self.rebuild()
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

        self.rebuild()
        threading.Timer(0.05, self.autoplay_handler, args=(self,)).start()

    def set_angle(self, angle):
        self.angle = angle

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
        self.rebuild()                              # Rebuild with new scale value
        return QMainWindow.resizeEvent(self, a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        Window close event handler
        :param a0: some argument
        :return: void
        """
        self.player_started = False
        self.config.save()

        return QMainWindow.closeEvent(self, a0)

    def rebuild(self):
        self.generator.run()
