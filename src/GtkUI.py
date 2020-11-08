#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf, GLib
from pathlib import Path
from PIL import Image
import os, io, array, json, locale
import Loader_MiBand4, Loader_MiBand5, DirObserver

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

APP_VERSION = "0.4"
SETTINGS_VERSION = 1
PV_DATA = {
    "H0": 1, "H1": 2, "M0": 3, "M1": 0, "S0": 3, "S1": 0,
    "DAY": 30, "MONTH": 2, "WEEKDAY": 6, "WEEKDAY_LANG": 2,
    "24H": False, "APM_CN": False, "APM_PM": True,
    "STEPS": 4000, "STEPS_TARGET": 8000,
    "PULSE": 120, "CALORIES": 420, "DISTANCE": 3.5,
    "BATTERY": 80, "LOCK": True, "MUTE": True,
    "BLUETOOTH": False, "ANIMATION_FRAME": 2, "ALARM_ON": True,
    "WEATHER_ICON": 0, "TEMP_CURRENT": -10, "TEMP_DAY": 15, "TEMP_NIGHT": -2
}

def img2buf(im):
    arr = array.array('B', im.tobytes())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)

def create_box(label):
    box = Gtk.Box()
    box.set_margin_top(10)
    label = Gtk.Label(label=label)
    label.set_halign(Gtk.Align.START)
    label.set_justify(Gtk.Justification.LEFT)
    box.pack_start(label, True, True, 0)
    return box

class AppWindow(Gtk.Window):
    def save_settings(self):
        data = {}
        data["version"] = SETTINGS_VERSION
        data["pv_data"] = PV_DATA
        data["path"] = self.path
        data["force_lang"] = self.force_lang
        data["compact_ui"] = self.compact_ui
        data["device_id"] = self.device_id
        with open(str(Path.home())+"/.mibandpreview.json", "w") as f:
            json.dump(data, f)

    def load_settings(self):
        global PV_DATA
        try:
            with open(str(Path.home())+"/.mibandpreview.json", "r") as f:
                if o["version"] != SETTINGS_VERSION: return
                o = json.load(f)
                self.compact_ui = o["compact_ui"]
                self.device_id = o["device_id"]
                self.force_lang = o["force_lang"]
                PV_DATA = o["pv_data"]
                self.bind_path(o["path"])
        except Exception as e:
            print(e)

    def load_locale(self):
        lang = locale.getdefaultlocale()[0][0:2]
        if self.force_lang:
            lang = self.force_lang

        print(lang)
        if not os.path.isfile(ROOT_DIR+"/lang/"+lang+".json"):
            print("Language ("+lang+") not supported. Failback to en...")
            lang = "en"

        with open(ROOT_DIR+"/lang/"+lang+".json") as f:
            self.locale = json.load(f)

    def reset_settings(self, a):
        os.remove(str(Path.home())+"/.mibandpreview.json")
        raise SystemExit

    def open_menu(self, widget):
        self.main_menu.set_relative_to(widget)
        self.main_menu.show_all()
        self.main_menu.popup()

    def open_langmenu(self, widget, aw):
        self.lang_menu.set_relative_to(aw)
        self.lang_menu.show_all()
        self.lang_menu.popup()

    def toggle_compact(self, btn):
        self.compact_ui = not self.compact_ui
        self.spawn()
        self.save_settings()

    def set_lang(self, widget, value):
        self.force_lang = value
        self.save_settings()
        self.destroy()

    def __init__(self):
        Gtk.Window.__init__(self, title="Mi Band Preview")

        self.is_watcher_added = False
        self.force_lang = False
        self.reclock = False
        self.compact_ui = False
        self.device_id = "mb4"
        self.path = ""

        self.mb5_oly = []
        self.hide_in_compact_mode = []

        self.load_settings()
        self.load_locale()

        # Window properties
        self.set_wmclass("mi-band-preview", "Mi Band Preview")
        self.set_role("mi-band-preview")
        self.set_resizable(False)
        self.set_icon_from_file(ROOT_DIR+"/res/icon48.png")

        # Headerbar
        self.header = Gtk.HeaderBar(show_close_button=True)
        self.set_titlebar(self.header)

        # Open menu
        menu_buttom = Gtk.ToolButton(icon_name="open-menu-symbolic")
        menu_buttom.connect("clicked", self.open_menu)
        self.header.pack_end(menu_buttom)

        # Open folder
        open_button = Gtk.Button(label=self.locale["header"]["open_button"])
        open_button.connect("clicked", self.open_file)
        self.header.pack_end(open_button)
        self.hide_in_compact_mode.append(open_button)

        # Language menu
        self.lang_menu = Gtk.Popover()
        langbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        langbox.set_size_request(240, 0)
        self.lang_menu.add(langbox)
        self.lang_menu.set_position(Gtk.PositionType.BOTTOM)

        for a in os.listdir(ROOT_DIR+"/lang"):
            lang = a.split(".")[0]
            btn = Gtk.ModelButton(label=lang)
            btn.set_alignment(0,0)
            btn.connect("clicked", self.set_lang, lang)
            langbox.pack_start(btn, False, True, 0)

        # Main Menu
        self.main_menu = Gtk.Popover()
        menubox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        menubox.set_size_request(240, 0)
        self.main_menu.add(menubox)
        self.main_menu.set_position(Gtk.PositionType.BOTTOM)

        openbtn = Gtk.ModelButton(label=self.locale["header"]["open_folder"])
        openbtn.set_alignment(0,0)
        openbtn.connect("clicked", self.open_file)
        menubox.pack_start(openbtn, False, True, 0)

        compactuibtn = Gtk.ModelButton(label=self.locale["header"]["toggle_compact"])
        compactuibtn.set_alignment(0,0)
        compactuibtn.connect("clicked", self.toggle_compact)
        menubox.pack_start(compactuibtn, False, True, 0)

        resetbtn = Gtk.ModelButton(label=self.locale["header"]["reset_settings"])
        resetbtn.set_alignment(0,0)
        resetbtn.connect("clicked", self.reset_settings)
        menubox.pack_start(resetbtn, False, True, 0)

        resetbtn = Gtk.ModelButton(label=self.locale["header"]["language"])
        resetbtn.set_alignment(0,0)
        resetbtn.connect("clicked", self.open_langmenu, menu_buttom)
        menubox.pack_start(resetbtn, False, True, 0)

        about_btn = Gtk.ModelButton(label=self.locale["header"]["about_app"])
        about_btn.set_alignment(0,0)
        about_btn.connect("clicked", self.show_about)
        menubox.pack_start(about_btn, False, True, 0)

        # Root box
        self.root_box = Gtk.Box(spacing=2)
        self.add(self.root_box)

        # Image view
        self.image = Gtk.Image.new_from_file(ROOT_DIR+"/res/no_file.png")
        self.root_box.add(self.image)

        # Settings box
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        settings_box.set_size_request(720, 480)
        settings_box.set_margin_end(10)
        settings_box.set_margin_start(10)
        self.root_box.add(settings_box)
        self.hide_in_compact_mode.append(settings_box)

        # Device select button
        devices = self.locale["device_names"]
        switchroot = create_box(self.locale["settings_groups"]["device"])
        switchbox = Gtk.Box(spacing=5)
        switchroot.add(switchbox)
        settings_box.add(switchroot)

        self.device_buttons = {}
        for a in devices:
            btn = Gtk.ToggleButton(label=devices[a])
            btn.connect("toggled", self.on_device_switch, a)
            switchbox.add(btn)
            self.device_buttons[a] = btn

        # Time input
        timeroot = create_box(self.locale["settings_groups"]["time"])
        settings_box.add(timeroot)

        hours = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=(PV_DATA['H0']*10+PV_DATA["H1"]),
            lower=0, upper=23
        ))
        hours.set_increments(1.00, 5.00)
        hours.set_numeric(True)
        hours.connect("value-changed", self.set_splitnumber_var, "H")
        timeroot.add(hours)

        minues = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=(PV_DATA['M0']*10+PV_DATA["M1"]),
            lower=0, upper=59
        ))
        minues.set_increments(1.00, 5.00)
        minues.set_numeric(True)
        minues.connect("value-changed", self.set_splitnumber_var, "M")
        timeroot.add(minues)

        seconds = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=(PV_DATA['S0']*10+PV_DATA["S1"]),
            lower=0, upper=59
        ))
        seconds.set_increments(1.00, 5.00)
        seconds.set_numeric(True)
        seconds.connect("value-changed", self.set_splitnumber_var, "S")
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
        dateroot = create_box(self.locale["settings_groups"]["date"])
        settings_box.add(dateroot)

        day = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["DAY"],
            lower=1, upper=31
        ))
        day.set_increments(1.00, 5.00)
        day.set_numeric(True)
        day.connect("value-changed", self.set_int_prop, "DAY")
        dateroot.add(day)

        month = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["MONTH"],
            lower=1, upper=12
        ))
        month.set_increments(1.00, 5.00)
        month.set_numeric(True)
        month.connect("value-changed", self.set_int_prop, "MONTH")
        dateroot.add(month)

        weekdays = Gtk.ListStore(str)
        for a in self.locale["weekdays"]:
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
        stepsroot = create_box(self.locale["settings_groups"]["steps"])
        settings_box.add(stepsroot)

        steps = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["STEPS"],
            lower=0, upper=20000
        ))
        steps.set_increments(1, 15)
        steps.set_numeric(True)
        steps.connect("value-changed", self.set_int_prop, "STEPS")
        stepsroot.add(steps)

        stepstarget = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["STEPS_TARGET"],
            lower=0, upper=20000
        ))
        stepstarget.set_increments(1.00, 15.00)
        stepstarget.set_numeric(True)
        stepstarget.connect("value-changed", self.set_int_prop, "STEPS_TARGET")
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

        # Misc
        box = create_box(self.locale["settings_groups"]["misc"])
        settings_box.add(box)

        pulse = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["PULSE"],
            lower=-1, upper=300
        ))
        pulse.set_increments(1, 5)
        pulse.set_numeric(True)
        pulse.connect("value-changed", self.set_int_prop, "PULSE")
        box.add(pulse)

        calories = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["CALORIES"],
            lower=0, upper=5000
        ))
        calories.set_increments(1, 10)
        calories.set_numeric(True)
        calories.connect("value-changed", self.set_int_prop, "CALORIES")
        box.add(calories)

        frame = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["ANIMATION_FRAME"],
            lower=0, upper=50
        ))
        frame.set_increments(1, 10)
        frame.set_numeric(True)
        frame.connect("value-changed", self.set_int_prop, "ANIMATION_FRAME")
        box.add(frame)

        # Status
        box = create_box(self.locale["settings_groups"]["status"])
        settings_box.add(box)

        battery = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["BATTERY"],
            lower=0, upper=100
        ))
        battery.set_increments(1, 10)
        battery.set_numeric(True)
        battery.connect("value-changed", self.set_int_prop, "BATTERY")
        box.add(battery)

        btn = Gtk.ToggleButton(label=self.locale["status_checkboxes"]["bt"])
        btn.set_active(PV_DATA["BLUETOOTH"])
        btn.connect("toggled", self.set_bool_prop, "BLUETOOTH")
        box.add(btn)

        btn = Gtk.ToggleButton(label=self.locale["status_checkboxes"]["mute"])
        btn.set_active(PV_DATA["MUTE"])
        btn.connect("toggled", self.set_bool_prop, "MUTE")
        box.add(btn)

        btn = Gtk.ToggleButton(label=self.locale["status_checkboxes"]["lock"])
        btn.set_active(PV_DATA["LOCK"])
        btn.connect("toggled", self.set_bool_prop, "LOCK")
        box.add(btn)

        btn = Gtk.ToggleButton(label=self.locale["status_checkboxes"]["alarm"])
        btn.set_active(PV_DATA["ALARM_ON"])
        btn.connect("toggled", self.set_bool_prop, "ALARM_ON")
        self.mb5_oly.append(btn)
        box.add(btn)

        # Weather
        box = create_box(self.locale["settings_groups"]["weather"])
        self.mb5_oly.append(box)
        settings_box.add(box)

        prop = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["WEATHER_ICON"],
            lower=0, upper=25
        ))
        prop.set_increments(1, 2)
        prop.set_numeric(True)
        prop.connect("value-changed", self.set_int_prop, "WEATHER_ICON")
        box.add(prop)

        prop = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["TEMP_CURRENT"],
            lower=-50, upper=40
        ))
        prop.set_increments(1, 10)
        prop.set_numeric(True)
        prop.connect("value-changed", self.set_int_prop, "TEMP_CURRENT")
        box.add(prop)

        prop = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["TEMP_DAY"],
            lower=-50, upper=40
        ))
        prop.set_increments(1, 10)
        prop.set_numeric(True)
        prop.connect("value-changed", self.set_int_prop, "TEMP_DAY")
        box.add(prop)

        prop = Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=PV_DATA["TEMP_NIGHT"],
            lower=-50, upper=40
        ))
        prop.set_increments(1, 10)
        prop.set_numeric(True)
        prop.connect("value-changed", self.set_int_prop, "TEMP_NIGHT")
        box.add(prop)

    def spawn(self):
        self.show_all()
        self.set_device(self.device_id)

        if self.compact_ui:
            self.hide_all_in(self.hide_in_compact_mode)
            self.header.set_title("")
        else:
            self.header.set_title("Mi Band Preview")
            self.show_all_in(self.hide_in_compact_mode)

        self.rebuild()

    def show_about(self,a):
        dialog = Gtk.AboutDialog(
            transient_for=self,
            logo=GdkPixbuf.Pixbuf.new_from_file(ROOT_DIR+"/res/icon96.png")
        )
        dialog.set_program_name("Mi Band Preview")
        dialog.set_version(APP_VERSION)
        dialog.set_website('https://github.com/melianmiko/MiBandPreview4Linux')
        dialog.set_authors(['MelianMiko'])
        dialog.set_license("Licensed under Apache 2.0")
        dialog.run()
        dialog.destroy()

    def on_device_switch(self, widget, value):
        if self.reclock: return
        self.reclock = True
        self.set_device(value)
        self.reclock = False

    def hide_all_in(self, array):
        for a in array: a.hide()

    def show_all_in(self, array):
        for a in array: a.show()

    def set_device(self, value):
        if value == "mb5": self.show_all_in(self.mb5_oly)
        else: self.hide_all_in(self.mb5_oly)

        for a in self.device_buttons:
            self.device_buttons[a].set_active(a == value)

        self.device_id = value
        self.save_settings()
        self.rebuild()

    def set_bool_prop(self, widget, tag):
        PV_DATA[tag] = widget.get_active()
        self.rebuild()

    def distance_changed(self, adj):
        v = adj.get_value();
        v = round(v, 3)
        PV_DATA["DISTANCE"] = v
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
            id = self.locale["weekdays"].index(weekday)
            PV_DATA["WEEKDAY"] = id
            self.rebuild()

    def set_int_prop(self, adj, key):
        v = adj.get_value_as_int()
        PV_DATA[key] = v
        self.rebuild()

    def set_splitnumber_var(self, adj, prefix):
        v = adj.get_value_as_int()
        h0 = v // 10
        h1 = v-(h0*10)
        PV_DATA[prefix+"0"] = h0
        PV_DATA[prefix+"1"] = h1
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
            print("Stopping previous watcher...")
            self.watcher.stop()

        self.watcher = DirObserver.new(path, self)
        self.is_watcher_added = True

        self.path = path
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

    def on_change(self):
        print("Refreshing preview...")
        self.rebuild()

win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.spawn()

Gtk.main()

print("Finishing...")
if win.is_watcher_added:
    win.watcher.stop()
