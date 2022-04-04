from PyQt5.QtCore import QTime, QDate
from PyQt5.QtWidgets import QTimeEdit

from mibandpreview import MiBandPreview
from mibandpreview_qt import ui_frames


def create(context):
    return LoaderUIAdapter(context, context.loader)


class LoaderUIAdapter:
    def __init__(self, context: ui_frames.Ui_MainWindow, loader: MiBandPreview):
        self.context = context
        self.loader = loader

    def read_ui(self):
        loader = self.loader

        # Date-time
        self._read_time(self.context.edit_time, "")
        self._read_time(self.context.edit_alarm_time, "alarm_")
        self._read_time(self.context.edit_tz1, "tz1_")
        self._read_time(self.context.edit_tz2, "tz2_")
        date = self.context.edit_date.date()        # type: QDate
        loader.set_property("year", date.year())
        loader.set_property("month", date.month())
        loader.set_property("day", date.day())

        # Date-time (extra)
        loader.set_property("24h", 1 if self.context.edit_am_pm.currentIndex() == 2 else 0)
        loader.set_property("am_pm", self.context.edit_am_pm.currentIndex())
        loader.set_property("weekday", self.context.edit_weekday.currentIndex()+1)

        # Status
        loader.set_property("status_battery", self.context.edit_battery.value())
        loader.set_property("status_lock", 1 if self.context.edit_lock.isChecked() else 0)
        loader.set_property("status_mute", 1 if self.context.edit_mute.isChecked() else 0)
        loader.set_property("status_bluetooth", 1 if self.context.edit_bluetooth.isChecked() else 0)
        loader.set_property("status_alarm", 1 if self.context.edit_alarm.isChecked() else 0)
        loader.set_property("status_timezone", 0 if self.context.edit_no_timezone.isChecked() else 1)

        # Activity
        loader.set_property("steps", self.context.edit_steps.value())
        loader.set_property("target_steps", self.context.edit_target_steps.value())
        loader.set_property("distance", self.context.edit_distance.value())
        loader.set_property("use_mil", self.context.edit_distance_unit.currentIndex())
        loader.set_property("calories", self.context.edit_calories.value())
        loader.set_property("heart_rate", self.context.edit_bpm.value())
        loader.set_property("pai", self.context.edit_pai.value())

        # Weather
        loader.set_property("weather_current", int(self.context.edit_t_now.value()))
        loader.set_property("weather_day", int(self.context.edit_t_day.value()))
        loader.set_property("weather_night", int(self.context.edit_t_night.value()))
        loader.set_property("weather_icon", self.context.edit_w_icon.currentIndex())
        loader.set_property("weather_humidity", int(self.context.edit_humidity.value()))
        loader.set_property("weather_uv", int(self.context.edit_uv_index.value()))
        loader.set_property("weather_wind", int(self.context.edit_wind.value()))

        loader.set_property("language", int(self.context.edit_language.currentIndex()))
        loader.set_property("mask_type", self.context.view_mask_type.currentIndex())

        return loader.config_export()

    def load_config(self):
        self.context.interactive = False
        loader = self.loader

        # Date-time
        self._update_time(self.context.edit_time, "", 12, 30, 45)
        self._update_time(self.context.edit_alarm_time, "alarm_", 7, 30, 0)
        self._update_time(self.context.edit_tz1, "tz1_", 22, 00, 0)
        self._update_time(self.context.edit_tz2, "tz2_", 6, 30, 0)
        date = QDate()
        date.setDate(loader.get_property("year", 2021),
                     loader.get_property("month", 2),
                     loader.get_property("day", 12))
        self.context.edit_date.setDate(date)

        # Date-time (extra)
        am_pm = 2
        if loader.get_property("24h", 0) == 0:
            am_pm = loader.get_property("am_pm", 0)
        self.context.edit_am_pm.setCurrentIndex(am_pm)
        self.context.edit_weekday.setCurrentIndex(loader.get_property("weekday", 2)-1)
        self.context.edit_language.setCurrentIndex(loader.get_property("language", 2))

        # Status
        self.context.edit_battery.setValue(loader.get_property("status_battery", 60))
        self.context.edit_bluetooth.setChecked(loader.get_property("status_bluetooth", 0) == 1)
        self.context.edit_lock.setChecked(loader.get_property("status_lock", 1) == 1)
        self.context.edit_mute.setChecked(loader.get_property("status_mute", 1) == 1)
        self.context.edit_alarm.setChecked(loader.get_property("status_alarm", 1) == 1)
        self.context.edit_no_timezone.setChecked(loader.get_property("status_timezone", 1) == 0)

        # Activity
        self.context.edit_steps.setValue(loader.get_property("steps", 6000))
        self.context.edit_target_steps.setValue(loader.get_property("target_steps", 9000))
        self.context.edit_distance.setValue(loader.get_property("distance", 12.1))
        self.context.edit_distance_unit.setCurrentIndex(loader.get_property("use_mil", 0))
        self.context.edit_calories.setValue(loader.get_property("calories", 600))
        self.context.edit_bpm.setValue(loader.get_property("heart_rate", 90))
        self.context.edit_pai.setValue(loader.get_property("pai", 88))

        # Weather
        self.context.edit_t_now.setValue(loader.get_property("weather_current", -2))
        self.context.edit_t_day.setValue(loader.get_property("weather_day", 10))
        self.context.edit_t_night.setValue(loader.get_property("weather_night", 10))
        self.context.edit_w_icon.setCurrentIndex(loader.get_property("weather_icon", 0))
        self.context.edit_humidity.setValue(loader.get_property("weather_humidity", 40))
        self.context.edit_uv_index.setValue(loader.get_property("weather_uv", 10))
        self.context.edit_wind.setValue(loader.get_property("weather_wind", 25))

        # Other
        self.context.view_mask_type.setCurrentIndex(loader.get_property("mask_type", 1))

        self.context.interactive = True

    def _read_time(self, field: QTimeEdit, prefix: str):
        time = field.time()
        self.loader.set_property(prefix + "hours", time.hour())
        self.loader.set_property(prefix + "minutes", time.minute())
        self.loader.set_property(prefix + "seconds", time.second())

    def _update_time(self, field: QTimeEdit, prefix: str, h: int, m: int, s: int):
        time = QTime()
        time.setHMS(self.loader.get_property(prefix + "hours", h),
                    self.loader.get_property(prefix + "minutes", m),
                    self.loader.get_property(prefix + "seconds", s))
        field.setTime(time)
