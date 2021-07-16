#!/usr/bin/env python3
import imgcompare
import sys
import os
from . import tools, open_dir

from PIL import Image

failed_templates = []
mb6_mask = Image.open(tools.get_root() + "/res/mb6_mask.png").convert("L")

app_config = {
    "hours": 0, "minutes": 0,
    "weekday": 3, "day": 6, "month": 1,
    "heart_rate": -1, "steps": 500, "pai": 3,
    "status_battery": 100, "status_mute": 1,
    "status_bluetooth": 1, "status_lock": 0,
    "calories": 34, "distance": 0.75,
    "weather_humidity": 5,
    "weather_icon": 0, "weather_wind": 1,
    "weather_current": -100, "weather_uv": 2,
    "weather_day": -15, "weather_night": -24,
    "status_alarm": 0, "status_timezone": 0
}


def compare_images(a, b):
    return imgcompare.image_diff_percent(a, b)


def get_valid_preview(path):
    for a in os.listdir(path):
        if "_animated" in a:
            return path + "/" + a
    raise Exception("Preview not found")


def process_wf(path, root, name):
    print("---- processing " + path)

    # Get valid preview
    valid = get_valid_preview(path)
    print("- Valid preview file " + valid)
    valid = Image.open(valid)
    valid.seek(0)
    valid = valid.convert("RGBA")

    # Spawn our preview
    loader = open_dir(path)
    loader.config_import(app_config)
    print("- detected device model: " + loader.get_property("device", "auto"))
    our = loader.render()

    # Round corners on valid preview (mb6 only)
    if loader.get_property("device", "auto") == "miband6":
        print("- Rounding corners for valid preview...")
        valid.putalpha(mb6_mask)

    # Compare
    diff = compare_images(valid, our)
    print("- diff " + str(diff))
    if diff > 4:
        failed_templates.append(name)

    # Build user_preview
    p = Image.new("RGBA", (valid.size[0] + our.size[0], valid.size[1]))
    tools.add_to_canvas(p, valid, (0, 0))
    tools.add_to_canvas(p, our, (valid.size[0], 0))
    p.save(root + "/" + name + "_test.png")

    print("")


def main(test_root):
    path = os.path.realpath(test_root)
    for a in os.listdir(path):
        if os.path.isdir(path + "/" + a):
            process_wf(path + "/" + a, path, a)

    # Print failed
    print("===========================")
    print("")
    print("Failed templates")
    for a in failed_templates:
        print("  - " + a)


if __name__ == "__main__.py":
    if len(sys.argv) < 2:
        print("Usage: ./test.py [WF_LIBRARY]")
        raise SystemExit()
    main(sys.argv[1])
