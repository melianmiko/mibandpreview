#!/bin/python3
import Loader_MiBand4

data = {
    "H0": 1, "H1": 2, "M0": 3, "M1": 0, "S0": 3, "S1": 0,
    "DAY": 30, "MONTH": 2, "WEEKDAY": 6, "WEEKDAY_LANG": 2,
    "STEPS": 4000, "STEPS_TARGET": 8000,
    "PULSE": 120, "CALORIES": 420, "DISTANCE": 3.5,
    "24H": False, "APM_CN": False, "APM_PM": True,
    "BATTERY": 80, "LOCK": True, "MUTE": True,
    "BLUETOOTH": False, "ANIMATION_FRAME": 2
}

loader = Loader_MiBand4.from_path(".")
loader.setSettings(data)
loader.render().save("../preview.png")
