import json
import pathlib
import sys

CONFIG_FILENAME = "mi_band_preview_qt.json"
CONFIG_VERSION = 1
storage = {}


def get(key, default_value):
    if key not in storage:
        return default_value

    return storage[key]


def put(key, value):
    storage[key] = value
    return value


def wipe():
    storage.clear()
    save()


def get_data_dir():
    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".config"

    return home


def init():
    path = get_data_dir() / CONFIG_FILENAME
    if path.is_file():
        with open(str(path), "r") as f:
            saved_storage = json.loads(f.read())
            if saved_storage["_version"] == CONFIG_VERSION:
                storage.update(saved_storage)


def save():
    path = get_data_dir() / CONFIG_FILENAME

    storage["_version"] = CONFIG_VERSION
    with open(str(path), "w") as f:
        f.write(json.dumps(storage))


init()
