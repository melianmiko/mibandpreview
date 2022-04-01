import os
from pathlib import Path

VERSION = "1.1"
APP_VERSION = "v" + VERSION

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = str(Path.home())+"/.mi_band_preview.json"
SETTINGS_VER = 5

LINK_GITHUB = "https://github.com/melianmiko/mibandpreview"
LINK_WEBSITE = "https://melianmiko.ru/mibandpreview"
