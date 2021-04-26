#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf, GLib
from pathlib import Path
from PIL import Image
from ctypes import cdll
import os, io, array, json, locale, threading, locale, gettext, platform

os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.getcwd(), 'cacert.pem')
import urllib.request, certifi, time
import DirObserver, mibandpreview

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

APP_VERSION = "v0.6"
SETTINGS_VERSION = 2

def img2buf(im):
    arr = array.array('B', im.tobytes())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)

def load_translations():
    locale.setlocale(locale.LC_ALL, '')
    print(locale.getlocale())

class MiBandPreviewApp:
    def __init__(self):
        load_translations()

        self.builder = Gtk.Builder()
        self.builder.set_translation_domain("mibandpreview")
        self.builder.add_from_file(ROOT_DIR+"/res/app.glade")
        self.builder.connect_signals(self)

        self.builder.get_object("preview_host_big").set_from_file(ROOT_DIR+"/res/no_file.png")
        self.builder.get_object("preview_host_small").set_from_file(ROOT_DIR+"/res/no_file.png")
        self.builder.get_object("main_window").set_wmclass("mi-band-preview", "Mi Band Preview")
        self.builder.get_object("main_window_compact").set_wmclass("mi-band-preview", "Mi Band Preview")

        self.loader = mibandpreview.create()

        self.path = ""
        #self.watcher = False
        self.is_active = True
        self.is_expanded = True
        #self.is_watcher_added = False
        self.allow_interact = False
        self.current_frame = [False, 0, 0, 0, 0]
        self.is_animation_complete = [False, False, False, False, False]
        self.set_device("Mi Band 4")
        self.preview = False
        self.last_wdtrigger = 0

        self.load_settings()
        self.restore_data()
        self.rebuild()

        self.gif_autoplay()

        # Check for updates
        self.builder.get_object("new_version_message").hide()
        print(platform.system())
        try:
            if platform.system() == "Windows":
                res = urllib.request.urlopen(
                    "https://gitlab.com/api/v4/projects/melianmiko%2Fmibandpreview/releases",
                    timeout=3
                    )
                res = json.loads(res.read())[0]
                if not res["tag_name"] == APP_VERSION:
                    print("New version: "+APP_VERSION+" != "+res["tag_name"])
                    self.builder.get_object("new_version_message").show()
        except Exception as e: print(e)

    def start(self):
        self.current_window = self.builder.get_object("main_window" if self.is_expanded else "main_window_compact")
        self.current_window.show()

    # Events
    def on_update_confirm(self, *args):
        pass

    def on_update_ignore(self, *args):
        self.builder.get_object("new_version_message").hide()

    def gif_autoplay(self):
        if not self.is_active: return
        rebuild_required = False

        for a in range(1,5):
            enabled = self.builder.get_object("gif_switch"+str(a)).get_active()
            if enabled:
                self.current_frame[a] += 1
                if self.is_animation_complete[a]: self.current_frame[a] = 0
                rebuild_required = True

        if rebuild_required: self.rebuild()

        threading.Timer(0.25, self.gif_autoplay).start()

    def on_exit(self, *args):
        self.is_active = False
        self.allow_interact = False
        self.current_window.hide()
        if self.is_watcher_added:
            self.watcher.stop()
        self.save_settings()
        Gtk.main_quit(*args)

    def on_change(self):
        t = time.time()

        if t-self.last_wdtrigger < 1:
            return

        if self.allow_interact:
            print("watchdog triggered, reloading...")
            threading.Timer(0.5, self.full_reload, args=(self,)).start()
            self.last_wdtrigger = t

    def sth_changed(self, *args):
        if self.allow_interact:
            self.read_new_data()
            self.rebuild()

    def gif_settings_changed(self, *args):
        for a in range(1, 5):
            obj = self.builder.get_object("frame_input"+str(a))
            self.current_frame[a] = obj.get_adjustment().get_value()
        self.sth_changed()

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
        #if self.is_watcher_added:
            #print("Stopping previous watcher...")
            #self.watcher.stop()

        if path == "" or not os.path.isdir(path):
            print("Empty or invalid path, ignoring...")
            return

        #self.watcher = DirObserver.new(path, self)
        #self.is_watcher_added = True
        self.path = path

        self.loader.bind_path(path)
        self.rebuild()

    def set_device(self, device_name):
        self.allow_interact = False
        self.device_id = device_name
        if device_name == "Mi Band 4":
            self.device_name = "miband4"
            self.builder.get_object("device_picker").set_active(0)
            self.builder.get_object("alarm_toggle").hide()
            self.builder.get_object("pai_label").hide()
            self.builder.get_object("pai_input").hide()
            self.builder.get_object("distance_type_picker").hide()
            self.builder.get_object("weather_settings").hide()
            self.rebuild()
        elif device_name == "Mi Band 5":
            self.device_name = "miband5"
            self.builder.get_object("device_picker").set_active(1)
            self.builder.get_object("alarm_toggle").show()
            self.builder.get_object("pai_label").show()
            self.builder.get_object("pai_input").show()
            self.builder.get_object("distance_type_picker").show()
            self.builder.get_object("weather_settings").show()
            self.rebuild()
        elif device_name == "Mi Band 6":
            self.device_name = "miband6"
            self.builder.get_object("device_picker").set_active(2)
            self.builder.get_object("alarm_toggle").show()
            self.builder.get_object("pai_label").show()
            self.builder.get_object("pai_input").show()
            self.builder.get_object("distance_type_picker").show()
            self.builder.get_object("weather_settings").show()
            self.rebuild()
        self.allow_interact = True

    def full_reload(self, *args):
        self.loader.load_data()
        self.rebuild()

    def rebuild(self, *args):
        if self.path == "": return
        try:
            self.loader.set_property("device", self.device_name)
            img = self.loader.render()

            img, state = self.loader.render_with_animation_frame(self.current_frame)
            self.setup_animations_ui()
            self.is_animation_complete = state
            
            if self.device_id == "Mi Band 6":
                img = img.resize((round(img.size[0]*1.5), round(img.size[1]*1.5)), resample=Image.BOX)
            else:
                img = img.resize((img.size[0]*2, img.size[1]*2), resample=Image.BOX)
            buf = img2buf(img)
            
            self.builder.get_object("preview_host_big").set_from_pixbuf(buf)
            self.builder.get_object("preview_host_small").set_from_pixbuf(buf)
        except Exception as e:
            print(e)
            self.builder.get_object("preview_host_big").set_from_file(ROOT_DIR+"/res/error.png")
            self.builder.get_object("preview_host_small").set_from_file(ROOT_DIR+"/res/error.png")

    def setup_animations_ui(self):
        count = self.loader.get_animations_count()
        for a in range(1, 5):
            obj = self.builder.get_object("gif_box"+str(a))
            if a <= count: obj.show()
            else: obj.hide()

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
        dialog.set_website('https://melianmiko.ru/mibandpreview')
        dialog.set_authors(['MelianMiko'])
        dialog.set_license("Licensed under Apache 2.0")
        dialog.run()
        dialog.destroy()

    # Settings storage
    def load_settings(self):
        try:
            with open(str(Path.home())+"/.mibandpreview.json", "r") as f:
                o = json.load(f)
                if o["version"] != SETTINGS_VERSION:
                    print("Settings file ignored, invalid version")
                    return
                self.set_device(o["device_id"])
                self.loader.config_import(o["pv_data"])
                self.bind_path(o["path"])
        except Exception as e:
            print(e)

    def save_settings(self):
        data = {}
        data["version"] = SETTINGS_VERSION
        data["pv_data"] = self.loader.config_export()
        data["path"] = self.path
        data["device_id"] = self.device_id
        with open(str(Path.home())+"/.mibandpreview.json", "w") as f:
            json.dump(data, f)
            print("Settings saved, have a nice day =)")

    def reset_settings(self, *args):
        self.current_window.hide()
        #if self.is_watcher_added:
            #self.watcher.stop()

        if os.path.isfile(str(Path.home())+"/.mibandpreview.json"):
            os.remove(str(Path.home())+"/.mibandpreview.json")

        Gtk.main_quit(*args)

    # Data processing
    def restore_data(self):
        self.allow_interact = False
        b = self.builder
        l = self.loader
        b.get_object("hours_spin").get_adjustment().set_value(l.get_property("hours", 12))
        b.get_object("minutes_spin").get_adjustment().set_value(l.get_property("minutes", 30))
        b.get_object("seconds_spin").get_adjustment().set_value(l.get_property("seconds", 45))
        b.get_object("date_day_spin").get_adjustment().set_value(l.get_property("day", 15))
        b.get_object("date_month_spin").get_adjustment().set_value(l.get_property("month", 2))
        b.get_object("weekday_combo").set_active(l.get_property("weekday", 2)-1)
        b.get_object("weekday_lang_combo").set_active(l.get_property("lang_weekday", 2))
        apm = 0
        if not l.get_property("24h", 0):
            apm = l.get_property("ampm", 0)+1
            if l.get_property("lang_ampm", 0): apm += 2
        b.get_object("ampm_mode").set_active(apm)
        b.get_object("battery_spin").get_adjustment().set_value(l.get_property("status_battery", 60))
        b.get_object("bluetooth_toggle").set_active(l.get_property("status_bluetooth", 0))
        b.get_object("lock_toggle").set_active(l.get_property("status_lock", 0))
        b.get_object("mute_toggle").set_active(l.get_property("status_mute", 0))
        b.get_object("alarm_toggle").set_active(l.get_property("status_alarm", 1))
        b.get_object("steps_input").get_adjustment().set_value(l.get_property("steps", 6000))
        b.get_object("steps_target_input").get_adjustment().set_value(l.get_property("target_steps", 9000))
        b.get_object("distance_input").get_adjustment().set_value(l.get_property("distance", 14.2))
        b.get_object("calories_input").get_adjustment().set_value(l.get_property("calories", 529))
        b.get_object("bpm_input").get_adjustment().set_value(l.get_property("heartrate", 60))
        b.get_object("pai_input").get_adjustment().set_value(l.get_property("pai", 88))
        b.get_object("t_now_input").get_adjustment().set_value(l.get_property("weather_current", -5))
        b.get_object("t_day_input").get_adjustment().set_value(l.get_property("weather_day", 10))
        b.get_object("t_night_input").get_adjustment().set_value(l.get_property("weather_night", -15))
        b.get_object("humidity_input").get_adjustment().set_value(l.get_property("weather_humidity", 60))
        b.get_object("weather_icon_input").set_active(l.get_property("weather_icon", 2))

        self.allow_interact = True

    def read_new_data(self):
        b = self.builder
        l = self.loader
        data = {}

        l.set_property("hours", b.get_object("hours_spin").get_adjustment().get_value())
        l.set_property("minutes", b.get_object("minutes_spin").get_adjustment().get_value())
        l.set_property("seconds", b.get_object("seconds_spin").get_adjustment().get_value())
        l.set_property("day", int(b.get_object("date_day_spin").get_adjustment().get_value()))
        l.set_property("month", int(b.get_object("date_month_spin").get_adjustment().get_value()))
        l.set_property("weekday", int(b.get_object("weekday_combo").get_active())+1)
        l.set_property("lang_weekday", b.get_object("weekday_lang_combo").get_active())

        val = b.get_object("ampm_mode").get_active_text()
        l.set_property("24h", 1 if "24h" in val else 0)
        l.set_property("lang_ampm", 1 if "CN" in val else 0)
        l.set_property("ampm", 1 if "PM" in val else 0)

        l.set_property("status_battery", int(b.get_object("battery_spin").get_adjustment().get_value()))
        l.set_property("status_bluetooth", b.get_object("bluetooth_toggle").get_active())
        l.set_property("status_mute", b.get_object("mute_toggle").get_active())
        l.set_property("status_lock", b.get_object("lock_toggle").get_active())
        l.set_property("status_alarm", b.get_object("alarm_toggle").get_active())
        l.set_property("steps", int(b.get_object("steps_input").get_adjustment().get_value()))
        l.set_property("target_steps", int(b.get_object("steps_target_input").get_adjustment().get_value()))
        l.set_property("distance", b.get_object("distance_input").get_adjustment().get_value())
        l.set_property("calories", int(b.get_object("calories_input").get_adjustment().get_value()))
        l.set_property("heartrate", int(b.get_object("bpm_input").get_adjustment().get_value()))
        l.set_property("pai", int(b.get_object("pai_input").get_adjustment().get_value()))

        l.set_property("weather_current", int(b.get_object("t_now_input").get_adjustment().get_value()))
        l.set_property("weather_day", int(b.get_object("t_day_input").get_adjustment().get_value()))
        l.set_property("weather_night", int(b.get_object("t_night_input").get_adjustment().get_value()))
        l.set_property("weather_humidity", int(b.get_object("humidity_input").get_adjustment().get_value()))
        l.set_property("weather_icon", int(b.get_object("weather_icon_input").get_active()))

if __name__ == "__main__":
    app = MiBandPreviewApp()
    app.start()
    Gtk.main()
