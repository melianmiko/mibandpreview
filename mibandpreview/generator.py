import json
import os
import string
from PIL import Image

from . import loader_miband4
from . import loader_miband5
from . import loader_miband6


class MiBandPreview:
    config = {}
    images = {}
    dir = ""
    target = ""

    def __init__(self, target="", device="auto", fix_missing=False, no_mask=False):
        """
        Default constructor
        :param target: target watchface DIR path
        :param device: device, auto detect by default
        :param fix_missing: ignore missing files flag
        :param no_mask: don't use Mi Band 6 maask flag
        """
        self.fix_missing = fix_missing
        self.no_mask = no_mask
        self.properties = {"device": device}
        self.placeholder = Image.new("RGBA", (0, 0))

        if not target == "":
            self.bind_path(target)

    def bind_path(self, target):
        self.dir = target
        self.load_data()

        if self.get_property("device", "auto") == "auto":
            self.detect_device()

    def load_data(self):
        self.config = {}
        self.images = {}

        for f in os.listdir(self.dir):
            if os.path.splitext(self.dir + "/" + f)[1] == ".json":
                with open(self.dir + "/" + f, "r") as jsf:
                    self.config = json.load(jsf)
                    break

        for a in os.listdir(self.dir):
            aa = a.split(".")
            if len(aa) > 1:
                if aa[1] == "png":
                    fn = a.split(".")[0]
                    if len(fn) == 4 and all(c in string.digits for c in fn):
                        img = Image.open(self.dir + "/" + fn + ".png")
                        img = img.convert("RGBA")
                        self.images[int(fn)] = img

    def get_property(self, key, default_value):
        if key not in self.properties:
            return default_value
        return self.properties[key]

    def set_property(self, key, val):
        self.properties[key] = val

    def config_export(self):
        return self.properties

    def config_import(self, p):
        for a in p:
            self.properties[a] = p[a]

    def get_resource(self, index):
        index = int(index)

        if index not in self.images:
            if self.fix_missing:
                return self.placeholder
            else:
                raise Exception("Image with index " + str(index) + " not found")

        return self.images[index]

    def get_resources_set(self, start, count):
        out = []
        for a in range(count):
            out.append(self.get_resource(start + a))
        return out

    def detect_device(self):
        self.set_property("device", "miband4")

        if "Background" in self.config:
            if "Preview1" in self.config["Background"]:
                index = self.config["Background"]["Preview1"]["ImageIndex"]
                image = self.get_resource(index)
                if image.width == 110:
                    self.set_property("device", "miband6")
                else:
                    self.set_property("device", "miband5")

    def get_loader(self):
        device = self.get_property("device", "auto")

        if device == "auto":
            raise Exception("Device auto-detect failed")
        elif device == "miband4":
            loader = loader_miband4
        elif device == "miband5":
            loader = loader_miband5
        elif device == "miband6":
            loader = loader_miband6
        else:
            raise Exception("Loader for device " + device + " not found")

        return loader

    def render(self):
        loader = self.get_loader()
        return loader.render(self)

    def render_with_animation_frame(self, current_frame):
        loader = self.get_loader()
        img = self.render()

        return loader.draw_animation_layers(self, current_frame, img)

    def get_animations_count(self):
        if "Other" not in self.config:
            return 0

        if "Animation" not in self.config["Other"]:
            return 0

        if self.get_property("device", "auto") == "miband4":
            return 1

        return len(self.config["Other"]["Animation"])
