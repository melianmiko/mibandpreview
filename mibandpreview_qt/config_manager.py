import json
import os

from . import app_info


def create(app):
    return ConfigManager(app)


class ConfigManager:
    """
    This class contains config read/write handlers
    """
    def __init__(self, app):
        self.app = app

    def wipe(self):
        """
        Wipe all configs
        :return: void
        """
        with open(app_info.SETTINGS_PATH, "w") as f:
            f.write("{}")

    def save(self):
        """
        Save app info to file
        :return: void
        """
        try:
            settings = {
                "preview_data": self.app.loader.config_export(),
                "last_path": self.app.path,
                "angle": self.app.angle,
                "version": app_info.SETTINGS_VER,
                "update_checker_enabled": self.app.updater.update_checker_enabled
            }

            with open(app_info.SETTINGS_PATH, "w") as f:
                f.write(json.dumps(settings))
            print("Settings saved to " + app_info.SETTINGS_PATH)
        except Exception as e:
            print(e)
            print("Can't save settings")

    def load(self):
        """
        Load app settings
        :return: void
        """
        if not os.path.isfile(app_info.SETTINGS_PATH):
            return

        with open(app_info.SETTINGS_PATH, "r") as f:
            data = json.loads(f.read())

        try:
            if data["version"] != app_info.SETTINGS_VER:
                print("Ignoring settings file, version mismatch")
                return

            self.app.loader.config_import(data["preview_data"])
            self.app.bind_path(data["last_path"])
            self.app.set_angle(data["angle"])
            self.app.adapter.load_config()
            self.app.updater.update_checker_enabled = data["update_checker_enabled"]
        except Exception as e:
            print(e)
            print("Can't load settings")


