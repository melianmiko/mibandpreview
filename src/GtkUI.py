#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf, GLib
from watchdog.observers import Observer
from pathlib import Path
from PIL import Image
import os, io, array, json
import Loader_MiBand4, Loader_MiBand5

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PV_DATA = {
    "H0": 1, "H1": 2, "M0": 3, "M1": 0, "S0": 3, "S1": 0,
    "DAY": 30, "MONTH": 2, "WEEKDAY": 6, "WEEKDAY_LANG": 2,
    "24H": False, "APM_CN": False, "APM_PM": True,
    "STEPS": 4000, "STEPS_TARGET": 8000,
    "PULSE": 120, "CALORIES": 420, "DISTANCE": 3.5,
    "BATTERY": 80, "LOCK": True, "MUTE": True,
    "BLUETOOTH": False, "ANIMATION_FRAME": 2, "ALARM_ON": True
}

def img2buf(im):
    arr = array.array('B', im.tobytes())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)

class AppWindow(Gtk.Window):
    def save_settings(self):
        data = {}
        data["path"] = self.path
        data["pv_data"] = PV_DATA
        data["device_id"] = self.device_id
        with open(str(Path.home())+"/.mibandpreview.json", "w") as f:
            json.dump(data, f)

    def load_settings(self):
        global PV_DATA
        try:
            with open(str(Path.home())+"/.mibandpreview.json", "r") as f:
                o = json.load(f)
                self.path = o["path"]
                self.device_id = o["device_id"]
                PV_DATA = o["pv_data"]
                print(o)
        except Exception as e:
            print(e)

    def reset_settings(self, a):
        os.remove(str(Path.home())+"/.mibandpreview.json")
        raise SystemExit

    def __init__(self):
        Gtk.Window.__init__(self, title="Mi Band Preview")

        self.is_watcher_added = False
        self.reclock = False
        self.device_id = ""
        self.path = ""

        self.load_settings()

        self.set_wmclass("mi-band-preview", "Mi Band Preview")
        # self.set_keep_above(True)
        self.set_icon_from_file(ROOT_DIR+"/res/icon48.png")

        self.header = Gtk.HeaderBar(show_close_button=True)
        self.header.set_title("Mi Band Preview")
        self.set_titlebar(self.header)

        self.openButton = Gtk.Button(label="Open folder")
        self.openButton.connect("clicked", self.open_file)
        self.header.pack_start(self.openButton)

        self.about_btn = Gtk.Button(label="About")
        self.about_btn.connect("clicked", self.show_about)
        self.header.pack_end(self.about_btn)

        self.reset = Gtk.Button(label="Reset settings")
        self.reset.connect("clicked", self.reset_settings)
        self.header.pack_end(self.reset)

        self.root_box = Gtk.Box(spacing=2)
        self.add(self.root_box)

        self.image = Gtk.Image.new_from_file(ROOT_DIR+"/res/no_file.png")
        self.root_box.add(self.image)

        # Settings
        self.root_box.add(self.get_settings_box())
        self.set_device(self.device_id)

        self.set_resizable(False)
        self.rebuild()

    def show_about(self,a):
        dialog = Gtk.AboutDialog(
            transient_for=self,
            logo=GdkPixbuf.Pixbuf.new_from_file(ROOT_DIR+"/res/icon96.png")
        )
        dialog.set_program_name("Mi Band Preview")
        dialog.set_version('0.2')
        dialog.set_website('https://github.com/melianmiko/MiBandPreview4Linux')
        dialog.set_authors(['MelianMiko'])
        dialog.set_license("Licensed under Apache 2.0")
        dialog.run()
        dialog.destroy()

    def on_device_switch(self, widget, value):
        self.set_device(value)

    def set_device(self, value):
        if self.reclock: return
        self.reclock = True

        for a in self.device_buttons:
            self.device_buttons[a].set_active(a == value)

        self.device_id = value
        self.save_settings()
        self.reclock = False

        self.rebuild()

    def get_settings_box(self):
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        settings_box.set_size_request(540, 480)
        settings_box.set_margin_right(10)
        settings_box.set_margin_left(10)

        # Device select button
        devices = {
            "mb4": "Mi Band 4",
            "mb5": "Mi Band 5"
        }

        switchroot = Gtk.Box()
        switchroot.set_margin_top(10)
        switchlabel = Gtk.Label(label="Device:")
        switchlabel.set_alignment(0,0)
        switchbox = Gtk.Box(spacing=5)
        switchroot.pack_start(switchlabel, True, True, 0)
        switchroot.add(switchbox)
        settings_box.add(switchroot)

        self.device_buttons = {}
        for a in devices:
            btn = Gtk.ToggleButton(label=devices[a])
            btn.connect("toggled", self.on_device_switch, a)
            switchbox.add(btn)
            self.device_buttons[a] = btn

        # Time input
        timeroot = Gtk.Box()
        timeroot.set_margin_top(10)
        timelabel = Gtk.Label(label="Time:")
        timelabel.set_alignment(0,0)
        timeroot.pack_start(timelabel, True, True, 0)
        settings_box.add(timeroot)

        hours = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=(PV_DATA['H0']*10+PV_DATA["H1"]),
            lower=0, upper=24
        ))
        hours.set_increments(1.00, 5.00)
        hours.set_numeric(True)
        hours.connect("value-changed", self.hours_changed)
        timeroot.add(hours)

        minues = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=(PV_DATA['M0']*10+PV_DATA["M1"]),
            lower=0, upper=59
        ))
        minues.set_increments(1.00, 5.00)
        minues.set_numeric(True)
        minues.connect("value-changed", self.minues_changed)
        timeroot.add(minues)

        seconds = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=(PV_DATA['S0']*10+PV_DATA["S1"]),
            lower=0, upper=59
        ))
        seconds.set_increments(1.00, 5.00)
        seconds.set_numeric(True)
        seconds.connect("value-changed", self.seconds_changed)
        timeroot.add(seconds)

        apm_values = Gtk.ListStore(str)
        for a in ["OFF", "CN AM", "CN PM", "EU AM", "EU PM"]:
            apm_values.append([a])
        apm = Gtk.ComboBox.new_with_model(apm_values)
        apm.set_active(self.get_apm_value())
        apm.connect("changed", self.apm_changed)
        renderer_text = Gtk.CellRendererText()
        apm.pack_start(renderer_text, True)
        apm.add_attribute(renderer_text, "text", 0)
        timeroot.add(apm)

        # Date input
        dateroot = Gtk.Box()
        dateroot.set_margin_top(10)
        datelabel = Gtk.Label(label="Date:")
        datelabel.set_alignment(0,0)
        dateroot.pack_start(datelabel, True, True, 0)
        settings_box.add(dateroot)

        day = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["DAY"],
            lower=1, upper=31
        ))
        day.set_increments(1.00, 5.00)
        day.set_numeric(True)
        day.connect("value-changed", self.day_changed)
        dateroot.add(day)

        month = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["MONTH"],
            lower=1, upper=12
        ))
        month.set_increments(1.00, 5.00)
        month.set_numeric(True)
        month.connect("value-changed", self.month_changed)
        dateroot.add(month)

        weekdays = Gtk.ListStore(str)
        for a in WEEKDAY_NAMES:
            weekdays.append([a])
        weekday = Gtk.ComboBox.new_with_model(weekdays)
        weekday.set_active(PV_DATA["WEEKDAY"])
        weekday.connect("changed", self.weekday_changed)
        renderer_text = Gtk.CellRendererText()
        weekday.pack_start(renderer_text, True)
        weekday.add_attribute(renderer_text, "text", 0)
        dateroot.add(weekday)

        wd_langs = Gtk.ListStore(str)
        for a in ["CN1", "CN2", "EU"]:
            wd_langs.append([a])
        wdlang = Gtk.ComboBox.new_with_model(wd_langs)
        wdlang.set_active(PV_DATA["WEEKDAY_LANG"])
        wdlang.connect("changed", self.wdlang_changed)
        renderer_text = Gtk.CellRendererText()
        wdlang.pack_start(renderer_text, True)
        wdlang.add_attribute(renderer_text, "text", 0)
        dateroot.add(wdlang)

        # Steps input
        stepsroot = Gtk.Box()
        stepsroot.set_margin_top(10)
        stepslabel = Gtk.Label(label="Steps, target, km:")
        stepslabel.set_alignment(0,0)
        stepsroot.pack_start(stepslabel, True, True, 0)
        settings_box.add(stepsroot)

        steps = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["STEPS"],
            lower=0, upper=20000
        ))
        steps.set_increments(1, 15)
        steps.set_numeric(True)
        steps.connect("value-changed", self.steps_changed)
        stepsroot.add(steps)

        stepstarget = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["STEPS_TARGET"],
            lower=0, upper=20000
        ))
        stepstarget.set_increments(1.00, 15.00)
        stepstarget.set_numeric(True)
        stepstarget.connect("value-changed", self.stepstarget_changed)
        stepsroot.add(stepstarget)

        distance = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["DISTANCE"],
            lower=0.0, upper=30.0, step_increment=0.2
        ), climb_rate=1.0, digits=2)
        distance.set_wrap(True)
        distance.set_increments(0.2, 1)
        distance.set_numeric(True)
        distance.connect("value-changed", self.distance_changed)
        stepsroot.add(distance)

        # Pulse, calories, GIF frame
        box = Gtk.Box()
        box.set_margin_top(10)
        label = Gtk.Label(label="Pulse, kcal, frame: ")
        label.set_alignment(0,0)
        box.pack_start(label, True, True, 0)
        settings_box.add(box)

        pulse = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["PULSE"],
            lower=-1, upper=300
        ))
        pulse.set_increments(1, 5)
        pulse.set_numeric(True)
        pulse.connect("value-changed", self.pulse_change)
        box.add(pulse)

        calories = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["CALORIES"],
            lower=0, upper=5000
        ))
        calories.set_increments(1, 10)
        calories.set_numeric(True)
        calories.connect("value-changed", self.calories_change)
        box.add(calories)

        frame = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["ANIMATION_FRAME"],
            lower=0, upper=50
        ))
        frame.set_increments(1, 10)
        frame.set_numeric(True)
        frame.connect("value-changed", self.frame_changed)
        box.add(frame)

        # Status
        box = Gtk.Box()
        box.set_margin_top(10)
        label = Gtk.Label(label="Status: ")
        label.set_alignment(0,0)
        box.pack_start(label, True, True, 0)
        settings_box.add(box)

        battery = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["BATTERY"],
            lower=0, upper=100
        ))
        battery.set_increments(1, 10)
        battery.set_numeric(True)
        battery.connect("value-changed", self.battery_changed)
        box.add(battery)

        btn = Gtk.ToggleButton(label="BT")
        btn.set_active(PV_DATA["BLUETOOTH"])
        btn.connect("toggled", self.bt_changed, "BLUETOOTH")
        box.add(btn)

        btn = Gtk.ToggleButton(label="MUTE")
        btn.set_active(PV_DATA["MUTE"])
        btn.connect("toggled", self.bt_changed, "MUTE")
        box.add(btn)

        btn = Gtk.ToggleButton(label="LOCK")
        btn.set_active(PV_DATA["LOCK"])
        btn.connect("toggled", self.bt_changed, "LOCK")
        box.add(btn)

        btn = Gtk.ToggleButton(label="ALARM")
        btn.set_active(PV_DATA["ALARM_ON"])
        btn.connect("toggled", self.bt_changed, "ALARM_ON")
        box.add(btn)

        return settings_box

    def bt_changed(self, widget, tag):
        PV_DATA[tag] = widget.get_active()
        self.rebuild()

    def battery_changed(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["BATTERY"] = v
        self.rebuild()

    def frame_changed(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["ANIMATION_FRAME"] = v
        self.rebuild()

    def calories_change(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["CALORIES"] = v
        self.rebuild()

    def pulse_change(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["PULSE"] = v
        self.rebuild()

    def distance_changed(self, adj):
        v = adj.get_value();
        v = round(v, 3)
        PV_DATA["DISTANCE"] = v
        self.rebuild()

    def stepstarget_changed(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["STEPS_TARGET"] = v
        self.rebuild()

    def steps_changed(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["STEPS"] = v
        self.rebuild()

    def get_apm_value(self):
        if PV_DATA["24H"]: return 0
        if PV_DATA["APM_CN"] and not PV_DATA["APM_PM"]: return 1
        if PV_DATA["APM_CN"] and PV_DATA["APM_PM"]: return 2
        if not PV_DATA["APM_CN"] and not PV_DATA["APM_PM"]: return 3
        if not PV_DATA["APM_CN"] and PV_DATA["APM_PM"]: return 4

    def apm_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            apmval = model[tree_iter][0]
            PV_DATA["24H"] = (apmval == "OFF")
            PV_DATA["APM_CN"] = ('CN' in apmval)
            PV_DATA["APM_PM"] = ('PM' in apmval)
            self.rebuild()

    def wdlang_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            weekday = model[tree_iter][0]
            id = ["CN1", "CN2", "EU"].index(weekday)
            PV_DATA["WEEKDAY_LANG"] = id
            self.rebuild()

    def weekday_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            weekday = model[tree_iter][0]
            id = WEEKDAY_NAMES.index(weekday)
            PV_DATA["WEEKDAY"] = id
            self.rebuild()

    def day_changed(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["DAY"] = v
        self.rebuild()

    def month_changed(self, adj):
        v = adj.get_value_as_int()
        PV_DATA["MONTH"] = v
        self.rebuild()

    def hours_changed(self, adj):
        v = adj.get_value_as_int()
        h0 = v // 10
        h1 = v-(h0*10)
        PV_DATA["H0"] = h0
        PV_DATA["H1"] = h1
        self.rebuild()

    def minues_changed(self, adj):
        v = adj.get_value_as_int()
        h0 = v // 10
        h1 = v-(h0*10)
        PV_DATA["M0"] = h0
        PV_DATA["M1"] = h1
        self.rebuild()

    def seconds_changed(self, adj):
        v = adj.get_value_as_int()
        h0 = v // 10
        h1 = v-(h0*10)
        PV_DATA["S0"] = h0
        PV_DATA["S1"] = h1
        self.rebuild()

    def open_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Choose an unpacked WF directory",
            parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER
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
            print("Stopping previouse watcher...")
            self.watcher.stop()

        self.watcher = Observer()
        self.watcher.schedule(self, path, recursive=True)
        self.watcher.start()
        self.is_watcher_added = True

        self.path = path
        self.rebuild()

    def dispatch(self, event):
        self.rebuild()

    def rebuild(self):
        if self.path == "": return
        try:
            if self.device_id == "mb4":
                loader = Loader_MiBand4.from_path(self.path)
            elif self.device_id == "mb5":
                loader = Loader_MiBand5.from_path(self.path)
            loader.setSettings(PV_DATA)
            img = loader.render()
            img = img.resize((img.size[0]*2, img.size[1]*2), resample=Image.BOX)
            buf = img2buf(img)
            self.image.set_from_pixbuf(buf)
            self.save_settings()
        except Exception as e:
            print(e)
            self.image.set_from_file(ROOT_DIR+"/res/error.png")

win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
