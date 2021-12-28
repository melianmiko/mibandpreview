import os
import traceback
import PIL.Image
from PyQt5.QtCore import QThread, pyqtSignal


def create(app):
    return PreviewThread(app)


class PreviewThread(QThread):
    image_ready = pyqtSignal(PIL.Image.Image)
    image_failed = pyqtSignal()
    image_missing = pyqtSignal()

    def __init__(self, app):
        """
        Default constructor
        :param app: context app class
        """
        super().__init__()
        self.app = app

    def get_scale_factor(self, size):
        """
        Calculate image scaling factor, fit to screen
        :param size: Image size data
        :return: integer
        """
        w = self.app.width() - self.app.tabWidget.width() - 20
        h = self.app.height() - 40
        ratio = min(w / size[0], h / size[1])
        ratio = round(ratio, 1)
        return ratio

    def run(self):
        """
        Render image and send result with signal
        :return: void
        """
        if self.app.path == "" or not os.path.isdir(self.app.path):
            # noinspection PyUnresolvedReferences
            self.image_missing.emit()
            return

        try:
            img, state = self.app.loader.render_with_animation_frame(self.app.frames)
            sf = self.get_scale_factor(img.size)
            angle = self.app.angle
            img = img.resize((round(img.size[0] * sf), round(img.size[1] * sf)), resample=PIL.Image.BOX)
            img = img.rotate(angle, expand=True)

            self.app.player_state = state
            # noinspection PyUnresolvedReferences
            self.image_ready.emit(img)
        except Exception as e:
            print("RENDER ERROR: "+str(e))
            traceback.print_exc()
            # noinspection PyUnresolvedReferences
            self.image_failed.emit()
