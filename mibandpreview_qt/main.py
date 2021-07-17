import os.path
import threading

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QFileSystemWatcher, QLocale, QTranslator, pyqtSignal, QLibraryInfo
from PyQt5.QtGui import QIcon

import mibandpreview
from .MainWindow import Ui_MainWindow
from . import UiHandler, app_info
from .update_checker import UpdateCheckerUI
from .config_manager import ConfigManager
from .preview_thread import PreviewThread


class MiBandPreviewApp(QMainWindow, Ui_MainWindow):
    path = ""
    frames = [0, 0, 0, 0, 0]
    player_toggle = [False, False, False, False, False]
    player_state = [False, False, False, False, False]
    player_started = False

    rebuild_required = pyqtSignal()

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
            print("Loading translation "+str(locale))
            translator.load(app_info.APP_ROOT+"/qt/app_"+locale_short+".qm")
            self.app.installTranslator(translator)

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

        self.updater = UpdateCheckerUI(self)                # Update checker module
        self.config = ConfigManager(self)                   # Config manager module
        self.generator = PreviewThread(self)

        self.loader = mibandpreview.MiBandPreview()         # type: mibandpreview.MiBandPreview
        self.watcher = QFileSystemWatcher()                 # type: QFileSystemWatcher
        self.handler = UiHandler.create(self)               # type: UiHandler

        self.bind_signals()

        self.handler.load_config()
        self.handler.read_ui()
        self.handler.set_no_preview()
        self.config.load()

        if self.updater.should_check_updates():
            self.updater.start()

    # noinspection PyUnresolvedReferences
    def bind_signals(self):
        """
        Bind signal listeners
        :return: void
        """
        self.watcher.directoryChanged.connect(self.on_file_change)
        self.watcher.fileChanged.connect(self.on_file_change)
        self.generator.image_ready.connect(self.handler.set_preview)
        self.generator.image_missing.connect(self.handler.set_no_preview)
        self.generator.image_failed.connect(self.handler.set_error_preview)

    def save_image(self, path):
        """
        Save current GUI image to file
        :param path: Target path
        :return: void
        """
        data = self.loader.render_with_animation_frame(self.frames)
        data[0].save(path)

    def rebuild(self):
        """
        Rebuild preview
        :return: void
        """
        self.generator.run()

    def bind_path(self, path):
        """
        Bind project path to application
        :param path: Target path
        :return: void
        """
        self.path = path

        if path == "":
            self.handler.set_no_preview()
            return

        for a in self.watcher.directories():
            self.watcher.removePath(a)

        self.watcher.addPath(path)
        self.loader.set_property("device", "auto")
        self.loader.bind_path(path)
        print("Using path: "+path)

        self.handler.setup_gif_ui()
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
            self.handler.set_error_preview()

    def autoplay_init(self):
        """
        Initialize GIF autoplay
        :return:
        """
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
