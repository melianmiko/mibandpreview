#!/bin/python3
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf, GLib
from watchdog.observers import Observer
from pathlib import Path
from PIL import Image
import os, io, array
import Loader_MiBand4

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PV_DATA = {
    "H0": 1, "H1": 2, "M0": 3, "M1": 0, "S0": 3, "S1": 0,
    "DAY": 30, "MONTH": 2, "WEEKDAY": 6, "WEEKDAY_LANG": 2,
    "STEPS": 4000, "STEPS_TARGET": 8000,
    "PULSE": 120, "CALORIES": 420, "DISTANCE": 3.5,
    "24H": False, "APM_CN": False, "APM_PM": True,
    "BATTERY": 80, "LOCK": True, "MUTE": True,
    "BLUETOOTH": False, "ANIMATION_FRAME": 2
}


def img2buf(im):
    arr = array.array('B', im.tobytes())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)

class AppWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Mi Band Preview")

        self.is_watcher_added = False

        self.set_wmclass("mi-band-preview", "Mi Band Preview")
        self.set_keep_above(True)
        self.set_icon_from_file(ROOT_DIR+"/docs/icon48.png")

        self.header = Gtk.HeaderBar(show_close_button=True)
        self.header.set_title("Mi Band Preview")
        self.set_titlebar(self.header)

        self.openButton = Gtk.Button(label="Open folder")
        self.openButton.connect("clicked", self.open_file)
        self.header.pack_end(self.openButton)

        self.root_box = Gtk.Box(spacing=2)
        self.add(self.root_box)

        self.image = Gtk.Image.new_from_file(ROOT_DIR+"/docs/no_file.png")
        self.image.set_size_request(240, 480)
        self.root_box.add(self.image)

        self.root_box.add(self.get_settings_box())

        self.set_resizable(False)

    def get_settings_box(self):
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        settings_box.set_size_request(400, 480)
        demo = Gtk.Label(label="Hello, World!")
        demo.set_alignment(0,0)
        settings_box.add(demo)
        return settings_box

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
        try:
            loader = Loader_MiBand4.from_path(self.path)
            loader.setSettings(PV_DATA)
            img = loader.render()
            img = img.resize((240, 480), resample=Image.BOX)
            buf = img2buf(img)
            self.image.set_from_pixbuf(buf)
        except Exception as e:
            print(e)
            self.image.set_from_file(ROOT_DIR+"/docs/error.png")

win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
