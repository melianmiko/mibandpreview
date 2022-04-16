import json
import os
import string

import PIL.Image
from PIL import Image

from . import loader_miband4, tools
from . import loader_miband5
from . import loader_miband6


class MiBandPreview:
    MASK_TYPE_NONE = 0
    MASK_TYPE_PERFECT = 1
    MASK_TYPE_SIMPLE = 2

    def __init__(self, target="", device="auto", fix_missing=False):
        """
        Default constructor
        :param target: target watchface DIR path
        :param device: device, auto detect by default
        :param fix_missing: ignore missing files flag
        """
        self.fix_missing = fix_missing
        self.config = {}
        self.images = {}
        self.path = ""
        self.path_json = ""
        self.target = ""

        self.placeholder = Image.new("RGBA", (0, 0))
        self.properties = {
            "device": device,
            "mask_type": self.MASK_TYPE_PERFECT
        }

        if not target == "":
            self.bind_path(target)

    def bind_json(self, file):
        self.path = os.path.dirname(file)
        self.path_json = file
        if not os.path.isfile(file) or file == "":
            # Unbind path
            self.config = {}
            self.images = {}

        self.load_data()
        if self.get_property("device", "auto") == "auto":
            self.detect_device()

    def bind_path(self, target):
        self.path = target
        self.find_json()
        if not os.path.isdir(target) or target == "":
            # Unbind path
            self.config = {}
            self.images = {}

        self.load_data()
        if self.get_property("device", "auto") == "auto":
            self.detect_device()

    def find_json(self):
        self.path_json = ""
        for f in os.listdir(self.path):
            if os.path.splitext(self.path + "/" + f)[1] == ".json":
                self.path_json = self.path + "/" + f
                break

    def load_json(self):
        data = tools.json_file_read(self.path_json)
        self.config = json.loads(data)

    def load_data(self):
        self.config = {}
        self.images = {}

        self.load_json()

        for a in os.listdir(self.path):
            aa = a.split(".")
            if len(aa) > 1:
                if aa[1] == "png":
                    fn = a.split(".")[0]
                    if len(fn) == 4 and all(c in string.digits for c in fn):
                        img = Image.open(self.path + "/" + fn + ".png")
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

    def get_mask(self):
        mask_type = self.get_property("mask_type", self.MASK_TYPE_PERFECT)
        if mask_type == self.MASK_TYPE_PERFECT:
            return Image.open(tools.get_root() + "/res/mb6_mask.png").convert("L")
        elif mask_type == self.MASK_TYPE_SIMPLE:
            return Image.open(tools.get_root() + "/res/mb6_mask_lite.png").convert("L")

        return None

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
