#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf, GLib
from pathlib import Path
from PIL import Image
import os, io, array, json, locale
import Loader_MiBand4, Loader_MiBand5, DirObserver

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

APP_VERSION = 0.5
SETTINGS_VERSION = 2
PV_DATA = {
    "H0": 1, "H1": 2, "M0": 3, "M1": 0, "S0": 3, "S1": 0,
    "DAY": 30, "MONTH": 2, "WEEKDAY": 4, "WEEKDAY_LANG": 2,
    "24H": False, "APM_CN": True, "APM_PM": True,
    "STEPS": 4000, "STEPS_TARGET": 8000,
    "PULSE": 120, "CALORIES": 420, "DISTANCE": 3.5,
    "BATTERY": 80, "LOCK": True, "MUTE": True,
    "BLUETOOTH": False, "ANIMATION_FRAME": 999, "ALARM_ON": True,
    "WEATHER_ICON": 3, "TEMP_CURRENT": -10, "TEMP_DAY": 15, "TEMP_NIGHT": -2,
    "PAI": 60, "HUMIDITY": 25
}

def img2buf(im):
    arr = array.array('B', im.tobytes())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)

class MiBandPreviewApp:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(self)

        self.builder.get_object("preview_host_big").set_from_file(ROOT_DIR+"/res/no_file.png")
        self.builder.get_object("preview_host_small").set_from_file(ROOT_DIR+"/res/no_file.png")
        self.builder.get_object("main_window").set_wmclass("mi-band-preview", "Mi Band Preview")
        self.builder.get_object("main_window_compact").set_wmclass("mi-band-preview", "Mi Band Preview")

        self.path = ""
        self.is_expanded = True
        self.is_watcher_added = False
        self.set_device("Mi Band 4")

        self.load_settings()
        self.restore_data()

    def start(self):
        self.current_window = self.builder.get_object("main_window" if self.is_expanded else "main_window_compact")
        self.current_window.show()

    # Events
    def on_exit(self, *args):
        self.current_window.hide()
        if self.is_watcher_added:
            self.watcher.stop()
        self.save_settings()
        Gtk.main_quit(*args)

    def on_change(self):
        self.sth_changed(0)

    def sth_changed(self, *args):
        if self.allow_interact:
            self.read_new_data()
            self.rebuild()

    def gif_settings_changed(self, *args):
        print(2)

    def on_device_select(self, *args):
        if self.allow_interact:
            new_device = self.builder.get_object("device_picker").get_active_text()
            self.set_device(new_device)

    def toggle_compact_mode(self, *args):
        self.is_expanded = not self.is_expanded
        self.current_window.hide()
        self.start()

    def show_open_dialog(self, *args):
        dialog = Gtk.FileChooserDialog(
            title="Choose an unpacked WF directory",
            parent=self.current_window, action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Open this folder", Gtk.ResponseType.OK
        )
        dialog.set_default_size(600, 300)
        dialog.set_current_folder(str(Path.home()))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self.bind_path(path)
        dialog.destroy()

    def bind_path(self, path):
        if self.is_watcher_added:
            print("Stopping previous watcher...")
            self.watcher.stop()

        self.watcher = DirObserver.new(path, self)
        self.is_watcher_added = True

        self.path = path
        self.rebuild()

    def set_device(self, device_name):
        self.allow_interact = False
        self.device_id = device_name
        if device_name == "Mi Band 4":
            self.Loader = Loader_MiBand4
            self.builder.get_object("device_picker").set_active(0)
            self.builder.get_object("alarm_toggle").hide()
            self.builder.get_object("pai_label").hide()
            self.builder.get_object("pai_input").hide()
            self.builder.get_object("distance_type_picker").hide()
            self.builder.get_object("weather_settings").hide()
            self.rebuild()
        elif device_name == "Mi Band 5":
            self.Loader = Loader_MiBand5
            self.builder.get_object("device_picker").set_active(1)
            self.builder.get_object("alarm_toggle").show()
            self.builder.get_object("pai_label").show()
            self.builder.get_object("pai_input").show()
            self.builder.get_object("distance_type_picker").show()
            self.builder.get_object("weather_settings").show()
            self.rebuild()
        self.allow_interact = True

    def rebuild(self):
        if self.path == "": return
        try:
            loader = self.Loader.from_path(self.path)
            loader.setSettings(PV_DATA)
            img = loader.render()
            img = img.resize((img.size[0]*2, img.size[1]*2), resample=Image.BOX)
            buf = img2buf(img)

            self.builder.get_object("preview_host_big").set_from_pixbuf(buf)
            self.builder.get_object("preview_host_small").set_from_pixbuf(buf)

            # self.save_settings()
        except Exception as e:
            print(e)
            self.builder.get_object("preview_host_big").set_from_file(ROOT_DIR+"/res/error.png")
            self.builder.get_object("preview_host_small").set_from_file(ROOT_DIR+"/res/error.png")

    def show_app_menu(self, *args):
        menu = self.builder.get_object("app_menu")
        menu.show_all()

    def show_about_dialog(self, *args):
        dialog = Gtk.AboutDialog(
            transient_for=self.current_window,
            logo=GdkPixbuf.Pixbuf.new_from_file(ROOT_DIR+"/res/icon96.png")
        )
        dialog.set_program_name("Mi Band Preview")
        dialog.set_version(str(APP_VERSION))
        dialog.set_website('https://github.com/melianmiko/MiBandPreview4Linux')
        dialog.set_authors(['MelianMiko'])
        dialog.set_license("Licensed under Apache 2.0")
        dialog.run()
        dialog.destroy()

    # Settings storage
    def load_settings(self):
        global PV_DATA
        try:
            with open(str(Path.home())+"/.mibandpreview.json", "r") as f:
                o = json.load(f)
                if o["version"] != SETTINGS_VERSION:
                    print("Settings file ignored, invalid version")
                    return
                self.set_device(o["device_id"])
                PV_DATA = o["pv_data"]
                self.bind_path(o["path"])
                self.rebuild()
        except Exception as e:
            print(e)

    def save_settings(self):
        data = {}
        data["version"] = SETTINGS_VERSION
        data["pv_data"] = PV_DATA
        data["path"] = self.path
        data["device_id"] = self.device_id
        with open(str(Path.home())+"/.mibandpreview.json", "w") as f:
            json.dump(data, f)
            print("Settings saved, have a nice day =)")

    def reset_settings(self, *args):
        self.current_window.hide()
        if self.is_watcher_added:
            self.watcher.stop()

        if os.path.isfile(str(Path.home())+"/.mibandpreview.json"):
            os.remove(str(Path.home())+"/.mibandpreview.json")

        Gtk.main_quit(*args)

    # Data processing
    def restore_data(self):
        self.allow_interact = False
        b = self.builder
        b.get_object("hours_spin").get_adjustment().set_value(PV_DATA["H0"]*10+PV_DATA["H1"])
        b.get_object("minutes_spin").get_adjustment().set_value(PV_DATA["M0"]*10+PV_DATA["M1"])
        b.get_object("seconds_spin").get_adjustment().set_value(PV_DATA["S0"]*10+PV_DATA["S1"])
        b.get_object("date_day_spin").get_adjustment().set_value(PV_DATA["DAY"])
        b.get_object("date_month_spin").get_adjustment().set_value(PV_DATA["MONTH"])
        b.get_object("weekday_combo").set_active(PV_DATA["WEEKDAY"])
        b.get_object("weekday_lang_combo").set_active(PV_DATA["WEEKDAY_LANG"])
        apm = 0
        if not PV_DATA["24H"]:
            apm = PV_DATA["APM_PM"]+1
            if PV_DATA["APM_CN"]: apm += 2
        b.get_object("ampm_mode").set_active(apm)
        b.get_object("battery_spin").get_adjustment().set_value(PV_DATA["BATTERY"])
        b.get_object("bluetooth_toggle").set_active(PV_DATA["BLUETOOTH"])
        b.get_object("lock_toggle").set_active(PV_DATA["LOCK"])
        b.get_object("mute_toggle").set_active(PV_DATA["MUTE"])
        b.get_object("alarm_toggle").set_active(PV_DATA["ALARM_ON"])
        b.get_object("steps_input").get_adjustment().set_value(PV_DATA["STEPS"])
        b.get_object("steps_target_input").get_adjustment().set_value(PV_DATA["STEPS_TARGET"])
        b.get_object("distance_input").get_adjustment().set_value(PV_DATA["DISTANCE"])
        b.get_object("calories_input").get_adjustment().set_value(PV_DATA["CALORIES"])
        b.get_object("bpm_input").get_adjustment().set_value(PV_DATA["PULSE"])
        b.get_object("pai_input").get_adjustment().set_value(PV_DATA["PAI"])
        b.get_object("t_now_input").get_adjustment().set_value(PV_DATA["TEMP_CURRENT"])
        b.get_object("t_day_input").get_adjustment().set_value(PV_DATA["TEMP_DAY"])
        b.get_object("t_night_input").get_adjustment().set_value(PV_DATA["TEMP_NIGHT"])
        b.get_object("humidity_input").get_adjustment().set_value(PV_DATA["HUMIDITY"])
        b.get_object("weather_icon_input").set_active(PV_DATA["WEATHER_ICON"])
        self.allow_interact = True

    def read_new_data(self):
        b = self.builder
        data = {}

        val = b.get_object("hours_spin").get_adjustment().get_value()
        data["H0"] = int(val // 10)
        data["H1"] = int(val-(data["H0"]*10))

        val = b.get_object("minutes_spin").get_adjustment().get_value()
        data["M0"] = int(val // 10)
        data["M1"] = int(val-(data["M0"]*10))

        val = b.get_object("seconds_spin").get_adjustment().get_value()
        data["S0"] = int(val // 10)
        data["S1"] = int(val-(data["S0"]*10))

        data["DAY"] = int(b.get_object("date_day_spin").get_adjustment().get_value())
        data["MONTH"] = int(b.get_object("date_month_spin").get_adjustment().get_value())
        data["WEEKDAY"] = int(b.get_object("weekday_combo").get_active())

        val = b.get_object("weekday_lang_combo").get_active_text()
        data["WEEKDAY_LANG"] = 0
        if "CN2" in val: data["WEEKDAY_LANG"] = 1
        if "INT" in val: data["WEEKDAY_LANG"] = 2

        val = b.get_object("ampm_mode").get_active_text()
        data["24H"] = 1 if "24h" in val else 0
        data["APM_CN"] = 1 if "CN" in val else 0
        data["APM_PM"] = 1 if "PM" in val else 0

        data["BATTERY"] = int(b.get_object("battery_spin").get_adjustment().get_value())
        data["BLUETOOTH"] = b.get_object("bluetooth_toggle").get_active()
        data["MUTE"] = b.get_object("mute_toggle").get_active()
        data["LOCK"] = b.get_object("lock_toggle").get_active()
        data["ALARM_ON"] = b.get_object("alarm_toggle").get_active()

        data["STEPS"] = int(b.get_object("steps_input").get_adjustment().get_value())
        data["STEPS_TARGET"] = int(b.get_object("steps_target_input").get_adjustment().get_value())
        data["DISTANCE"] = b.get_object("distance_input").get_adjustment().get_value()
        data["CALORIES"] = int(b.get_object("calories_input").get_adjustment().get_value())
        data["PULSE"] = int(b.get_object("bpm_input").get_adjustment().get_value())
        data["PAI"] = int(b.get_object("pai_input").get_adjustment().get_value())

        data["TEMP_CURRENT"] = int(b.get_object("t_now_input").get_adjustment().get_value())
        data["TEMP_DAY"] = int(b.get_object("t_day_input").get_adjustment().get_value())
        data["TEMP_NIGHT"] = int(b.get_object("t_night_input").get_adjustment().get_value())
        data["HUMIDITY"] = int(b.get_object("humidity_input").get_adjustment().get_value())
        data["WEATHER_ICON"] = int(b.get_object("weather_icon_input").get_active())

        data["ANIMATION_FRAME"] = 999

        global PV_DATA
        PV_DATA = data

if __name__ == "__main__":
    app = MiBandPreviewApp()
    app.start()
    Gtk.main()
