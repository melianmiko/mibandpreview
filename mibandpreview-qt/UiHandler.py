from PyQt5.QtCore import QTime, QDate
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
from PIL import Image
import os

import main

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RES_NO_IMAGE = APP_ROOT+"/res/no_file.png"
RES_ERROR_IMAGE = APP_ROOT+"/res/error.png"


def create(context):
    return UIHandler(context)


# noinspection PyArgumentList
def pil_to_qt(img):
    im = img.tobytes("raw", "RGBA")
    im = QImage(im, img.size[0], img.size[1], QImage.Format_ARGB32)
    im = QPixmap.fromImage(im)
    return im


class UIHandler:
    allow_interaction = True

    def __init__(self, context):
        self.context = context  # type: main.MiBandPreviewApp
        self._init_qt_connections()

    def _init_qt_connections(self):
        # File menu
        self.context.menu_file.aboutToShow.connect(self._on_file_menu_open)
        self.context.action_open.triggered.connect(self._on_project_open)
        self.context.action_refresh.triggered.connect(lambda i: self.context.rebuild())
        self.context.target_mb4.triggered.connect(lambda i: self._on_device_selected("miband4"))
        self.context.target_mb5.triggered.connect(lambda i: self._on_device_selected("miband5"))
        self.context.target_mb6.triggered.connect(lambda i: self._on_device_selected("miband6"))
        self.context.action_exit.triggered.connect(lambda i: self.context.exit())

        # Settings
        self.context.edit_time.userTimeChanged.connect(self._on_change)
        self.context.edit_date.userDateChanged.connect(self._on_change)
        self.context.edit_ampm.currentIndexChanged.connect(self._on_change)
        self.context.edit_24h.stateChanged.connect(self._on_change)
        self.context.edit_weekday.currentIndexChanged.connect(self._on_change)
        self.context.edit_wd_lang.currentIndexChanged.connect(self._on_change)
        self.context.edit_battery.valueChanged.connect(self._on_change)
        self.context.edit_bluetooth.stateChanged.connect(self._on_change)
        self.context.edit_lock.stateChanged.connect(self._on_change)
        self.context.edit_mute.stateChanged.connect(self._on_change)
        self.context.edit_alarm.stateChanged.connect(self._on_change)
        self.context.edit_steps.valueChanged.connect(self._on_change)
        self.context.edit_target_steps.valueChanged.connect(self._on_change)
        self.context.edit_bpm.valueChanged.connect(self._on_change)
        self.context.edit_distance.valueChanged.connect(self._on_change)
        self.context.edit_calories.valueChanged.connect(self._on_change)
        self.context.edit_pai.valueChanged.connect(self._on_change)
        self.context.edit_t_now.valueChanged.connect(self._on_change)
        self.context.edit_t_day.valueChanged.connect(self._on_change)
        self.context.edit_t_night.valueChanged.connect(self._on_change)
        self.context.edit_w_icon.currentIndexChanged.connect(self._on_change)
        self.context.edit_humidity.valueChanged.connect(self._on_change)

        # GIF
        self.context.anim_frame_0.valueChanged.connect(self._on_gif_change)
        self.context.anim_frame_1.valueChanged.connect(self._on_gif_change)
        self.context.anim_frame_2.valueChanged.connect(self._on_gif_change)
        self.context.anim_frame_3.valueChanged.connect(self._on_gif_change)
        self.context.anim_frame_4.valueChanged.connect(self._on_gif_change)
        self.context.anim_play_0.stateChanged.connect(self._on_gif_change)
        self.context.anim_play_1.stateChanged.connect(self._on_gif_change)
        self.context.anim_play_2.stateChanged.connect(self._on_gif_change)
        self.context.anim_play_3.stateChanged.connect(self._on_gif_change)
        self.context.anim_play_4.stateChanged.connect(self._on_gif_change)

    def set_no_preview(self):
        self.context.preview_host.setPixmap(pil_to_qt(Image.open(RES_NO_IMAGE)))

    def set_preview(self, img):
        self.context.preview_host.setPixmap(pil_to_qt(img))

    def get_user_settings(self):
        loader = self.context.loader

        # Date-time
        time = self.context.edit_time.time()        # type: QTime
        loader.set_property("hours", time.hour())
        loader.set_property("minutes", time.minute())
        loader.set_property("seconds", time.second())
        date = self.context.edit_date.date()        # type: QDate
        loader.set_property("year", date.year())
        loader.set_property("month", date.month())
        loader.set_property("day", date.day())

        # Date-time (extra)
        loader.set_property("24h", 1 if self.context.edit_24h.isChecked() else 0)
        loader.set_property("lang_ampm", 1 if self.context.edit_ampm.currentIndex() < 2 else 0)
        loader.set_property("ampm", 1 if self.context.edit_ampm.currentIndex() % 2 == 1 else 0)
        loader.set_property("weekday", self.context.edit_weekday.currentIndex())
        loader.set_property("lang_weekday", self.context.edit_wd_lang.currentIndex())

        # Status
        loader.set_property("status_battery", self.context.edit_battery.value())
        loader.set_property("status_lock", 1 if self.context.edit_lock.isChecked() else 0)
        loader.set_property("status_mute", 1 if self.context.edit_mute.isChecked() else 0)
        loader.set_property("status_bluetooth", 1 if self.context.edit_bluetooth.isChecked() else 0)
        loader.set_property("status_alarm", 1 if self.context.edit_alarm.isChecked() else 0)

        # Activity
        loader.set_property("steps", self.context.edit_steps.value())
        loader.set_property("target_steps", self.context.edit_target_steps.value())
        loader.set_property("distance", self.context.edit_distance.value())
        loader.set_property("calories", self.context.edit_calories.value())
        loader.set_property("heartrate", self.context.edit_bpm.value())
        loader.set_property("pai", self.context.edit_pai.value())

        # Weather
        loader.set_property("weather_current", self.context.edit_t_now.value())
        loader.set_property("weather_day", self.context.edit_t_day.value())
        loader.set_property("weather_night", self.context.edit_t_night.value())
        loader.set_property("weather_icon", self.context.edit_w_icon.currentIndex())
        loader.set_property("humidity", self.context.edit_humidity.value())

    def set_user_settings(self):
        self.allow_interaction = False
        loader = self.context.loader

        # Date-time
        time = QTime()
        time.setHMS(loader.get_property("hours", 12), loader.get_property("minutes", 30),
                    loader.get_property("seconds", 45))
        self.context.edit_time.setTime(time)
        date = QDate()
        date.setDate(loader.get_property("year", 2021), loader.get_property("month", 2), loader.get_property("day", 12))
        self.context.edit_date.setDate(date)

        # Date-time (extra)
        self.context.edit_24h.setChecked(loader.get_property("24h", 0) == 1)
        self.context.edit_ampm.setCurrentIndex(loader.get_property("lang_ampm", 0) * 2 + loader.get_property("ampm", 0))
        self.context.edit_weekday.setCurrentIndex(loader.get_property("weekday", 2))
        self.context.edit_wd_lang.setCurrentIndex(loader.get_property("lang_weekday", 2))

        # Status
        self.context.edit_battery.setValue(loader.get_property("status_battery", 60))
        self.context.edit_bluetooth.setChecked(loader.get_property("status_bluetooth", 0) == 1)
        self.context.edit_lock.setChecked(loader.get_property("status_lock", 1) == 1)
        self.context.edit_mute.setChecked(loader.get_property("status_mute", 1) == 1)
        self.context.edit_alarm.setChecked(loader.get_property("status_alarm", 1) == 1)

        # Activity
        self.context.edit_steps.setValue(loader.get_property("steps", 6000))
        self.context.edit_target_steps.setValue(loader.get_property("target_steps", 9000))
        self.context.edit_distance.setValue(loader.get_property("distance", 12.1))
        self.context.edit_calories.setValue(loader.get_property("calories", 600))
        self.context.edit_bpm.setValue(loader.get_property("heartrate", 90))
        self.context.edit_pai.setValue(loader.get_property("pai", 88))

        # Weather
        self.context.edit_t_now.setValue(loader.get_property("weather_current", -2))
        self.context.edit_t_day.setValue(loader.get_property("weather_day", 10))
        self.context.edit_t_night.setValue(loader.get_property("weather_night", 10))
        self.context.edit_w_icon.setCurrentIndex(loader.get_property("weather_icon", 0))
        self.context.edit_humidity.setValue(loader.get_property("weather_humidity", 40))

        self.allow_interaction = True

    def setup_gif_ui(self):
        c = self.context.loader.get_animations_count()
        t = self.context.player_toggle

        self.context.anim_frame_0.setEnabled(c > 0 and not t[0])
        self.context.anim_frame_1.setEnabled(c > 1 and not t[1])
        self.context.anim_frame_2.setEnabled(c > 2 and not t[2])
        self.context.anim_frame_3.setEnabled(c > 3 and not t[3])
        self.context.anim_frame_4.setEnabled(c > 4 and not t[4])

        self.context.anim_play_0.setEnabled(c > 0)
        self.context.anim_play_1.setEnabled(c > 1)
        self.context.anim_play_2.setEnabled(c > 2)
        self.context.anim_play_3.setEnabled(c > 3)
        self.context.anim_play_4.setEnabled(c > 4)

    def _on_gif_change(self):
        self.context.frames = [
            self.context.anim_frame_0.value(),
            self.context.anim_frame_1.value(),
            self.context.anim_frame_2.value(),
            self.context.anim_frame_3.value(),
            self.context.anim_frame_4.value()
        ]
        self.context.player_toggle = [
            self.context.anim_play_0.isChecked(),
            self.context.anim_play_1.isChecked(),
            self.context.anim_play_2.isChecked(),
            self.context.anim_play_3.isChecked(),
            self.context.anim_play_4.isChecked()
        ]
        self.context.rebuild()
        self.context.autoplay_init()

    def _on_change(self):
        if self.allow_interaction:
            self.context.on_ui_change()

    def _on_project_open(self):
        path = QFileDialog.getExistingDirectory(None,
                                                "Select unpacked (!) watchface folder",
                                                str(Path.home()), QFileDialog.ShowDirsOnly)
        if path == "":
            return
        self.context.bind_path(path)

    def _on_device_selected(self, value):
        self.context.loader.set_property("device", value)
        self.context.rebuild()

    def _on_file_menu_open(self):
        device = self.context.loader.get_property("device", "auto")
        self.context.target_mb4.setChecked(device == "miband4")
        self.context.target_mb5.setChecked(device == "miband5")
        self.context.target_mb6.setChecked(device == "miband6")