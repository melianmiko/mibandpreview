from . import tools
from PIL import Image


def draw_animation_layers(app, current_frame, img):
    """
    Draw animation layers to image
    :param app: context app
    :param current_frame: current frame counters array
    :param img: target image
    :return: new image and states array
    """
    config = app.config
    state = [False, False]

    if "Other" in config:
        if "Animation" in config["Other"]:
            if current_frame[0] < config["Other"]["Animation"]["AnimationImage"]["ImagesCount"]:
                tools.draw_static_object(
                    app, img,
                    config["Other"]["Animation"]["AnimationImage"],
                    value=current_frame[0]
                )
            else:
                state[1] = True

    return img, state


def render_background(app, canvas, config):
    # Background
    if "Background" in config:
        if "Image" in config["Background"]:
            tools.draw_static_object(
                app, canvas,
                config["Background"]["Image"]
            )


def render_time(app, canvas, config):
    if "Time" in config:
        if "Hours" in config["Time"]:
            if "Tens" in config["Time"]["Hours"]:
                tools.draw_static_object(
                    app, canvas,
                    config["Time"]["Hours"]["Tens"],
                    value=app.get_property("hours", 12) // 10
                )

            if "Ones" in config["Time"]["Hours"]:
                tools.draw_static_object(
                    app, canvas,
                    config["Time"]["Hours"]["Ones"],
                    value=app.get_property("hours", 12) % 10
                )

        if "Minutes" in config["Time"]:
            if "Tens" in config["Time"]["Minutes"]:
                tools.draw_static_object(
                    app, canvas,
                    config["Time"]["Minutes"]["Tens"],
                    value=app.get_property("minutes", 30) // 10
                )

            if "Ones" in config["Time"]["Minutes"]:
                tools.draw_static_object(
                    app, canvas,
                    config["Time"]["Minutes"]["Ones"],
                    value=app.get_property("minutes", 30) % 10
                )

        if "DelimiterImage" in config["Time"]:
            tools.draw_static_object(
                app, canvas,
                config["Time"]["DelimiterImage"]
            )


def render_heart(app, canvas, config):
    if "Heart" in config:
        if "Scale" in config["Heart"]:
            index = config["Heart"]["Scale"]["StartImageIndex"]
            segments = config["Heart"]["Scale"]["Segments"]
            value = app.get_property("heart_rate", 200)
            i = int(max(0, min(1, value / 202) * len(segments) - 1))
            if i <= len(segments):
                img = app.get_resource(index + i)
                xy = (int(segments[i]["X"]), int(segments[i]["Y"]))
                tools.add_to_canvas(canvas, img, xy)


def render_activity(app, canvas, config):
    """
    Draw activity counters
    :param app: context app
    :param canvas: target canvas
    :param config: watchface config
    :return: void
    """
    render_heart(app, canvas, config)
    if "Activity" in config:
        if "Steps" in config["Activity"]:
            tools.draw_adv_number(app, canvas, config["Activity"]["Steps"]["Number"],
                                  value=app.get_property("steps", 12345))

        if "Pulse" in config["Activity"]:
            tools.draw_adv_number(app, canvas, config["Activity"]["Pulse"]["Number"],
                                  value=app.get_property("heart_rate", 120))

        if "Distance" in config["Activity"]:
            dist = config["Activity"]["Distance"]
            tools.draw_adv_number(app, canvas, dist["Number"], value=app.get_property("distance", 14.25),
                                  dot=dist["DecimalPointImageIndex"], posix=dist["SuffixImageIndex"])

        if "Calories" in config["Activity"]:
            kcal = config["Activity"]["Calories"]
            tools.draw_adv_number(app, canvas, kcal["Number"], value=app.get_property("calories", 500),
                                  posix=kcal["SuffixImageIndex"])

    if "StepsProgress" in config:
        if "Linear" in config["StepsProgress"]:
            steps = app.get_property("steps", 6000)
            target = app.get_property("target_steps", 9000)
            tools.draw_steps_bar(
                app, canvas,
                config["StepsProgress"]["Linear"],
                min(1, steps / target)
            )


def render_date(app, canvas, config):
    """
    Draw date
    :param app: context app
    :param canvas: target canvas
    :param config: watchface config
    :return: void
    """
    month_leading_zero = False
    day_leading_zero = False
    if "Date" in config:
        if "MonthAndDay" in config["Date"]:
            if "TwoDigitsDay" in config["Date"]["MonthAndDay"]:
                day_leading_zero = config["Date"]["MonthAndDay"]["TwoDigitsDay"]

            if "TwoDigitsMonth" in config["Date"]["MonthAndDay"]:
                month_leading_zero = config["Date"]["MonthAndDay"]["TwoDigitsMonth"]

            if "OneLine" in config["Date"]["MonthAndDay"]:
                date = config["Date"]["MonthAndDay"]["OneLine"]["Number"]
                dot = -1
                if "DelimiterImageIndex" in date:
                    dot = date["DelimiterImageIndex"]

                tools.draw_date(
                    app, canvas, date,
                    app.get_property("month", 2),
                    app.get_property("day", 15), dot,
                    month_leading_zero, day_leading_zero
                )

            if "Separate" in config["Date"]["MonthAndDay"]:
                if "Month" in config["Date"]["MonthAndDay"]["Separate"]:
                    tools.draw_adv_number(app, canvas, config["Date"]["MonthAndDay"]["Separate"]["Month"],
                                          value=app.get_property("month", 12), digits=(2 if month_leading_zero else 1))
                if "Day" in config["Date"]["MonthAndDay"]["Separate"]:
                    tools.draw_adv_number(app, canvas, config["Date"]["MonthAndDay"]["Separate"]["Day"],
                                          value=app.get_property("day", 15), digits=(2 if day_leading_zero else 1))

        if "WeekDay" in config["Date"]:
            tools.draw_static_object(
                app, canvas, config["Date"]["WeekDay"],
                value=app.get_property("weekday", 3) - 1 + app.get_property("language", 2) * 7
            )

        if "DayAmPm" in config["Date"] and not app.get_property("24h", 0) == 1:
            apm = config["Date"]["DayAmPm"]
            val = app.get_property("am_pm", 0)
            lang = 1 if app.get_property("language", 0) < 2 else 0
            if val == 1 and lang == 1:
                index = apm["ImageIndexPMCN"]
            elif val == 0 and lang == 1:
                index = apm["ImageIndexAMCN"]
            elif val == 1 and lang == 0:
                index = apm["ImageIndexPMEN"]
            elif val == 0 and lang == 0:
                index = apm["ImageIndexAMEN"]
            else:
                raise Exception("Undefined AM/PM state")
            tools.add_to_canvas(
                canvas,
                app.get_resource(index),
                (int(apm["X"]), int(apm["Y"]))
            )


def render_status(app, canvas, config):
    if "Status" in config:
        if "DoNotDisturb" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["DoNotDisturb"] and app.get_property("status_mute", 1):
                tools.add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["DoNotDisturb"]["ImageIndexOn"]),
                    (
                        config["Status"]["DoNotDisturb"]["Coordinates"]["X"],
                        config["Status"]["DoNotDisturb"]["Coordinates"]["Y"]
                    )
                )

            if "ImageIndexOff" in config["Status"]["DoNotDisturb"] and not app.get_property("status_mute", 1):
                tools.add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["DoNotDisturb"]["ImageIndexOff"]),
                    (
                        config["Status"]["DoNotDisturb"]["Coordinates"]["X"],
                        config["Status"]["DoNotDisturb"]["Coordinates"]["Y"]
                    )
                )

        if "Lock" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["Lock"] and app.get_property("status_lock", 1):
                tools.add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Lock"]["ImageIndexOn"]),
                    (
                        config["Status"]["Lock"]["Coordinates"]["X"],
                        config["Status"]["Lock"]["Coordinates"]["Y"]
                    )
                )

            if "ImageIndexOff" in config["Status"]["Lock"] and not app.get_property("status_lock", 1):
                tools.add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Lock"]["ImageIndexOff"]),
                    (
                        config["Status"]["Lock"]["Coordinates"]["X"],
                        config["Status"]["Lock"]["Coordinates"]["Y"]
                    )
                )

        if "Bluetooth" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["Bluetooth"] and app.get_property("status_bluetooth", 1):
                tools.add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Bluetooth"]["ImageIndexOn"]),
                    (
                        config["Status"]["Bluetooth"]["Coordinates"]["X"],
                        config["Status"]["Bluetooth"]["Coordinates"]["Y"]
                    )
                )

            if "ImageIndexOff" in config["Status"]["Bluetooth"] and not app.get_property("status_bluetooth", 1):
                tools.add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Bluetooth"]["ImageIndexOff"]),
                    (
                        config["Status"]["Bluetooth"]["Coordinates"]["X"],
                        config["Status"]["Bluetooth"]["Coordinates"]["Y"]
                    )
                )

def render_battery(app, canvas, config):
        if "Status" not in config:
            return

        if "Battery" in config["Status"]:
            if "Text" in config["Status"]["Battery"]:
                tools.draw_adv_number(app, canvas, config["Status"]["Battery"]["Text"],
                                      value=app.get_property("status_battery", 60))

            if "Icon" in config["Status"]["Battery"]:
                value = app.get_property("status_battery", 60)
                value = int(config["Status"]["Battery"]["Icon"]["ImagesCount"] * (value / 100))
                if value >= config["Status"]["Battery"]["Icon"]["ImagesCount"]:
                    value = config["Status"]["Battery"]["Icon"]["ImagesCount"] - 1
                tools.draw_static_object(
                    app, canvas,
                    config["Status"]["Battery"]["Icon"],
                    value=value
                )


def render_analog_clock(app, canvas, config):
    if "AnalogDialFace" in config:
        hours = app.get_property("hours", 12)
        minutes = app.get_property("minutes", 30)
        seconds = app.get_property("seconds", 40)
        if "Hours" in config["AnalogDialFace"]:
            tools.draw_analog_dial(canvas, config["AnalogDialFace"]["Hours"], 30 * (hours + minutes / 60))

            if "CenterImage" in config["AnalogDialFace"]["Hours"]:
                tools.draw_static_object(
                    app, canvas,
                    config["AnalogDialFace"]["Hours"]["CenterImage"]
                )

        if "Minutes" in config["AnalogDialFace"]:
            tools.draw_analog_dial(canvas, config["AnalogDialFace"]["Minutes"], 30 * minutes)

            if "CenterImage" in config["AnalogDialFace"]["Minutes"]:
                tools.draw_static_object(
                    app, canvas,
                    config["AnalogDialFace"]["Minutes"]["CenterImage"]
                )

        if "Seconds" in config["AnalogDialFace"]:
            tools.draw_analog_dial(canvas, config["AnalogDialFace"]["Seconds"], 30 * seconds)

            if "CenterImage" in config["AnalogDialFace"]["Seconds"]:
                tools.draw_static_object(
                    app, canvas,
                    config["AnalogDialFace"]["Seconds"]["CenterImage"]
                )



def render_other(app, canvas, config):
    if "Other" in config:
        if "Animation" in config["Other"]:
            frame = app.get_property("animation_frame", 0)
            if frame < config["Other"]["Animation"]["AnimationImage"]["ImagesCount"]:
                tools.draw_static_object(
                    app, canvas,
                    config["Other"]["Animation"]["AnimationImage"],
                    value=frame
                )


def render(app):
    """
    Render preview for app
    :param app: context app
    :return: new image
    """
    # Spawn canvas, fill with black
    canvas = Image.new("RGBA", (120, 240))
    config = app.config

    render_background(app, canvas, config)
    render_time(app, canvas, config)
    render_activity(app, canvas, config)
    render_date(app, canvas, config)
    render_status(app, canvas, config)
    render_battery(app, canvas, config)
    render_analog_clock(app, canvas, config)
    render_other(app, canvas, config)

    return canvas
