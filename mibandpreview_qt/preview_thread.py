import logging
import os
import PIL.Image
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from mibandpreview_qt import pref_storage

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RES_NO_IMAGE = APP_ROOT+"/res/no_file.png"
RES_ERROR_IMAGE = APP_ROOT+"/res/error.png"

log = logging.getLogger("RenderThread")


def create(window):
    thread = PreviewThread(window)
    return thread


def pil_to_qt(img):
    r, g, b, a = img.split()
    im = Image.merge("RGBA", (b, g, r, a))
    im = im.tobytes("raw", "RGBA")
    im = QImage(im, img.size[0], img.size[1], QImage.Format_ARGB32)
    im = QPixmap.fromImage(im)
    return im


class PreviewThread(QThread):
    render_completed = pyqtSignal(QPixmap, bool)
    angles = [0, 90, 270]

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

    def get_scale_factor(self, size):
        """
        Calculate image scaling factor, fit to screen
        :param size: Image size data
        :return: integer
        """
        w = self.parent_window.width() - self.parent_window.tabWidget.width() - 20
        h = self.parent_window.height() - 40
        ratio = min(w / size[0], h / size[1])
        ratio = round(ratio, 1)
        return ratio

    # noinspection PyUnresolvedReferences,PyBroadException
    def bind_json(self, json_path):
        if not os.path.isfile(json_path):
            log.debug("bind failed, not a file: " + json_path)
            missing_img = pil_to_qt(Image.open(RES_NO_IMAGE))
            self.render_completed.emit(missing_img, False)
            return False

        try:
            self.parent_window.loader.bind_json(json_path)
            return True
        except Exception:
            log.exception("Can't bind this path")
            error_img = pil_to_qt(Image.open(RES_ERROR_IMAGE))
            self.render_completed.emit(error_img, False)
            return False

    # noinspection PyUnresolvedReferences,PyBroadException
    def run(self):
        """
        Render image and send result with signal
        :return: void
        """
        current_path = self.parent_window.loader.path
        log.debug("rendering for path " + current_path)

        if current_path == "" or not os.path.isdir(current_path):
            missing_img = pil_to_qt(Image.open(RES_NO_IMAGE))
            self.render_completed.emit(missing_img, False)
            return

        try:
            img, state = self.parent_window.loader.render_with_animation_frame(self.parent_window.frames)
            rotate_option = pref_storage.get("preview_rotate", 0)
            angle = self.angles[rotate_option]
            sf = self.get_scale_factor(img.size)

            img = img.resize((round(img.size[0] * sf), round(img.size[1] * sf)), resample=PIL.Image.BOX)
            img = img.rotate(angle, expand=True)
            img = pil_to_qt(img)

            self.parent_window.player_state = state
            self.render_completed.emit(img, True)
        except Exception:
            log.exception("render failed")
            error_img = pil_to_qt(Image.open(RES_ERROR_IMAGE))
            self.render_completed.emit(error_img, False)
