import os
import webbrowser

from PIL import Image
from PyQt5.QtGui import QImage, QPixmap

from mibandpreview_qt import app_info

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RES_NO_IMAGE = APP_ROOT+"/res/no_file.png"
RES_ERROR_IMAGE = APP_ROOT+"/res/error.png"


def pil_to_qt(img):
    r, g, b, a = img.split()
    im = Image.merge("RGBA", (b, g, r, a))
    im = im.tobytes("raw", "RGBA")
    im = QImage(im, img.size[0], img.size[1], QImage.Format_ARGB32)
    im = QPixmap.fromImage(im)
    return im


# noinspection PyMethodMayBeStatic,PyUnresolvedReferences,PyPep8Naming
class Ui_MainWindowWithSlots(object):
    frames = [0, 0, 0, 0, 0]
    player_toggle = [False, False, False, False, False]
    interactive = True

    def set_target_mb4(self):
        self.set_device("miband4")
        self.rebuild()

    def set_target_mb5(self):
        self.set_device("miband5")
        self.rebuild()

    def set_target_mb6(self):
        self.set_device("miband6")
        self.rebuild()

    def set_angle_0(self):
        self.set_angle(0)
        self.rebuild()

    def set_angle_90(self):
        self.set_angle(90)
        self.rebuild()

    def set_angle_270(self):
        self.set_angle(270)
        self.rebuild()

    def wipe_config(self):
        self.config.wipe()
        self.app.exit(0)

    def open_site(self):
        webbrowser.open(app_info.LINK_WEBSITE)

    def open_github(self):
        webbrowser.open(app_info.LINK_GITHUB)

    def ui_widget_changed(self):
        if self.interactive:
            self.handler.read_ui()
            self.rebuild()

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
        self.rebuild()
        self.autoplay_init()

    def set_preview_missing(self):
        self.preview_host.setPixmap(pil_to_qt(Image.open(RES_NO_IMAGE)))
        self.action_save.setEnabled(False)

    def set_preview_error(self):
        self.preview_host.setPixmap(pil_to_qt(Image.open(RES_ERROR_IMAGE)))
        self.action_save.setEnabled(False)

    def set_preview_image(self, img):
        self.preview_host.setPixmap(pil_to_qt(img))
        self.action_save.setEnabled(True)
