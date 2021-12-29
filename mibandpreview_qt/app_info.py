import os
from pathlib import Path

VERSION = "0.9"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = str(Path.home())+"/.mi_band_preview.json"
SETTINGS_VER = 5
APP_VERSION = "v" + VERSION

LINK_GITHUB = "https://github.com/melianmiko/mibandpreview"
LINK_WEBSITE = "https://melianmiko.ru/mibandpreview"

