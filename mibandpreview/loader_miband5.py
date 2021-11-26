from . import tools, loader_miband4
from PIL import Image, ImageDraw


def draw_animation_layers(app, current_frame, img):
    """
    Draw animation layers
    :param app: generator app context
    :param current_frame: array with number of current frames
    :param img: target image
    :return: new image and states array
    """
    config = app.config
    state = [False, False, False, False, False]

    n = 0
    if "Other" in config:
        if "Animation" in config["Other"]:
            for a in config["Other"]["Animation"]:
                if current_frame[n] < a["AnimationImages"]["ImagesCount"]:
                    tools.draw_static_object(app, img, a["AnimationImages"], value=current_frame[n])
                else:
                    state[n] = True
                n += 1

    return img, state


def render_background(config, canvas, app):
    """
    Render background module
    :param config: watchface config
    :param canvas: target canvas
    :param app: generator app context
    :return: void
    """
    draw = ImageDraw.Draw(canvas)
    if "Background" in config:
        if "BackgroundColor" in config["Background"]:
            color = "#" + config["Background"]["BackgroundColor"][2:]
            draw.rectangle((0, 0, canvas.size[0], canvas.size[1]), fill=color)
        if "Image" in config["Background"]:
            tools.draw_static_object(
                app, canvas,
                config["Background"]["Image"]
            )


def render_time(config, canvas, app):
    loader_miband4.render_time(app, canvas, config)

    if "Time" in config:
        if "TimeZone1" in config["Time"] and app.get_property("status_timezone", 1) == 1:
            a = round(app.get_property("hours", 12) + app.get_property("minutes", 30) / 100, 2)
            tools.draw_adv_number(app, canvas, config["Time"]["TimeZone1"], value=a, digits=2,
                                  dot=config["Time"]["TimeZone1DelimiterImage"])

        if "TimeZone1NoTime" in config["Time"] and app.get_property("status_timezone", 1) == 0:
            tools.draw_static_object(app, canvas, config["Time"]["TimeZone1NoTime"])

        if "TimeZone2" in config["Time"] and app.get_property("status_timezone", 1) == 1:
            a = round(app.get_property("hours", 12) + app.get_property("minutes", 30) / 100, 2)
            tools.draw_adv_number(app, canvas, config["Time"]["TimeZone2"], value=a, digits=2,
                                  dot=config["Time"]["TimeZone1DelimiterImage"])

        if "TimeZone2NoTime" in config["Time"] and app.get_property("status_timezone", 1) == 0:
            tools.draw_static_object(app, canvas, config["Time"]["TimeZone2NoTime"])


def render_activity(config, canvas, app):
    """
    Render activity module
    :param config: watchface config
    :param canvas: target canvas
    :param app: generator app context
    :return: void
    """
    if "Activity" in config:
        if "Steps" in config["Activity"]:
            prefix = -1
            if "PrefixImageIndex" in config["Activity"]["Steps"]:
                prefix = config["Activity"]["Steps"]["PrefixImageIndex"]

            tools.draw_adv_number(app, canvas, config["Activity"]["Steps"]["Number"],
                                  value=app.get_property("steps", 12345),
                                  prefix=prefix)

        if "Pulse" in config["Activity"]:
            prefix = -1
            if "PrefixImageIndex" in config["Activity"]["Pulse"]:
                prefix = config["Activity"]["Pulse"]["PrefixImageIndex"]

            if app.get_property("heart_rate", 120) > 0:
                tools.draw_adv_number(app, canvas, config["Activity"]["Pulse"]["Number"],
                                      value=app.get_property("heart_rate", 120), prefix=prefix)
            elif "NoDataImageIndex" in config["Activity"]["Pulse"]:
                img = app.get_resource(config["Activity"]["Pulse"]["NoDataImageIndex"])
                xy = tools.calculate_adv_position(config["Activity"]["Pulse"]["Number"], img.size)
                tools.add_to_canvas(canvas, img, xy)

        if "Distance" in config["Activity"]:
            value = app.get_property("distance", 14.2)
            dist = config["Activity"]["Distance"]
            posix = -1
            if "KmSuffixImageIndex" in dist:
                posix = dist["KmSuffixImageIndex"]

            tools.draw_adv_number(app, canvas, dist["Number"],
                                  value=round(value, 2),
                                  dot=dist["DecimalPointImageIndex"],
                                  posix=posix)

        if "Calories" in config["Activity"]:
            kcal = config["Activity"]["Calories"]
            posix = -1
            if "SuffixImageIndex" in kcal:
                posix = kcal["SuffixImageIndex"]
            tools.draw_adv_number(app, canvas, kcal["Text"], value=app.get_property("calories", 500), posix=posix)

        if "PAI" in config["Activity"]:
            tools.draw_adv_number(app, canvas, config["Activity"]["PAI"]["Number"], value=app.get_property("pai", 88))


def render_date(config, canvas, app):
    """
    Render date module
    :param config: watchface config
    :param canvas: target canvas
    :param app: generator app context
    :return: void
    """
    month_leading_zero = False
    day_leading_zero = False
    if "Date" in config:
        if "MonthAndDayAndYear" in config["Date"]:
            if "TwoDigitsDay" in config["Date"]["MonthAndDayAndYear"]:
                day_leading_zero = config["Date"]["MonthAndDayAndYear"]["TwoDigitsDay"]

            if "TwoDigitsMonth" in config["Date"]["MonthAndDayAndYear"]:
                month_leading_zero = config["Date"]["MonthAndDayAndYear"]["TwoDigitsMonth"]

            if "OneLine" in config["Date"]["MonthAndDayAndYear"]:
                date = config["Date"]["MonthAndDayAndYear"]["OneLine"]
                dot = -1
                if "DelimiterImageIndex" in date:
                    dot = date["DelimiterImageIndex"]

                tools.draw_date(
                    app, canvas, date["Number"],
                    app.get_property("month", 2),
                    app.get_property("day", 15),
                    dot,
                    month_leading_zero, day_leading_zero
                )

            if "OneLineWithYear" in config["Date"]["MonthAndDayAndYear"]:
                date = config["Date"]["MonthAndDayAndYear"]["OneLineWithYear"]
                dot = -1
                if "DelimiterImageIndex" in date:
                    dot = date["DelimiterImageIndex"]

                tools.draw_date(
                    app, canvas, date["Number"],
                    app.get_property("month", 2),
                    app.get_property("day", 15),
                    dot,
                    month_leading_zero, day_leading_zero,
                    year=app.get_property("year", 2021)
                )

            if "Separate" in config["Date"]["MonthAndDayAndYear"]:
                if "Month" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
                    tools.draw_adv_number(app, canvas, config["Date"]["MonthAndDayAndYear"]["Separate"]["Month"],
                                          value=app.get_property("month", 2), digits=(2 if month_leading_zero else 1))

                if "MonthsEN" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
                    tools.draw_static_object(
                        app, canvas,
                        config["Date"]["MonthAndDayAndYear"]["Separate"]["MonthsEN"],
                        value=app.get_property("month", 2)
                    )

                if "Day" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
                    tools.draw_adv_number(app, canvas, config["Date"]["MonthAndDayAndYear"]["Separate"]["Day"],
                                          value=app.get_property("day", 15), digits=(2 if day_leading_zero else 1))

        if "ENWeekDays" in config["Date"] and app.get_property("language", 2) == 2:
            tools.draw_static_object(
                app, canvas, config["Date"]["ENWeekDays"],
                value=app.get_property("weekday", 3) - 1
            )

        if "CN1WeekDays" in config["Date"] and app.get_property("language", 2) == 0:
            tools.draw_static_object(
                app, canvas, config["Date"]["CN1WeekDays"],
                value=app.get_property("weekday", 3) - 1
            )

        if "CN2WeekDays" in config["Date"] and app.get_property("language", 2) == 1:
            tools.draw_static_object(
                app, canvas, config["Date"]["CN2WeekDays"],
                value=app.get_property("weekday", 3) - 1
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
                raise Exception("Undefined AP/PM value")

            tools.add_to_canvas(
                canvas,
                app.get_resource(index),
                (int(apm["X"]), int(apm["Y"]))
            )

    if "WeekDaysIcons" in config:
        name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday = app.get_property("weekday", 3)
        target = name[weekday - 1]
        tools.draw_static_object(app, canvas, config["WeekDaysIcons"][target])


def render_activity_graph(config, canvas, app):
    loader_miband4.render_heart(app, canvas, config)

    if "StepsProgress" in config:
        steps = app.get_property("steps", 6000)
        target = app.get_property("target_steps", 9000)

        if "Linear" in config["StepsProgress"]:
            tools.draw_steps_bar(
                app, canvas,
                config["StepsProgress"]["Linear"],
                min(1, steps / target)
            )

        if "LineScale" in config["StepsProgress"]:
            current = int(config["StepsProgress"]["LineScale"]["ImagesCount"] * min(1, steps / target))
            if current >= config["StepsProgress"]["LineScale"]["ImagesCount"]:
                current = config["StepsProgress"]["LineScale"]["ImagesCount"] - 1
            tools.draw_static_object(
                app, canvas,
                config["StepsProgress"]["LineScale"],
                value=current
            )

    if "HeartProgress" in config:
        current_bpm = app.get_property("heart_rate", 200)

        if "Linear" in config["HeartProgress"]:
            index = config["HeartProgress"]["Linear"]["StartImageIndex"]
            segments = config["HeartProgress"]["Linear"]["Segments"]
            current = int(max(0, min(1, current_bpm / 202) * len(segments) - 1))
            for i in range(0, current):
                if i <= len(segments):
                    item = segments[i]
                    img = app.get_resource(index + i)
                    xy = (int(item["X"]), int(item["Y"]))
                    tools.add_to_canvas(canvas, img, xy)

        if "LineScale" in config["HeartProgress"]:
            count = config["HeartProgress"]["LineScale"]["ImagesCount"]
            current = int(max(0, min(1, current_bpm / 202) * count - 1))
            if current >= config["HeartProgress"]["LineScale"]["ImagesCount"]:
                current = config["HeartProgress"]["LineScale"]["ImagesCount"] - 1
            tools.draw_static_object(
                app, canvas,
                config["HeartProgress"]["LineScale"],
                value=current
            )

    if "CaloriesProgress" in config:
        current_kcal = app.get_property("calories", 500)
        if "LineScale" in config["CaloriesProgress"]:
            count = config["CaloriesProgress"]["LineScale"]["ImagesCount"]
            current = int(max(0, min(1, current_kcal / 1500) * count - 1))
            if current >= config["CaloriesProgress"]["LineScale"]["ImagesCount"]:
                current = config["CaloriesProgress"]["LineScale"]["ImagesCount"] - 1
            tools.draw_static_object(
                app, canvas,
                config["CaloriesProgress"]["LineScale"],
                value=current
            )


def render_status_icons(config, canvas, app):
    loader_miband4.render_status(app, canvas, config)


def render_battery(config, canvas, app):
    """
    Render battery module
    :param config: watchface config
    :param canvas: target canvas
    :param app: generator app context
    :return: void
    """
    if "Battery" in config:
        if "BatteryText" in config["Battery"]:
            posix = -1
            if "SuffixImageIndex" in config["Battery"]["BatteryText"]:
                posix = config["Battery"]["BatteryText"]["SuffixImageIndex"]
            tools.draw_adv_number(app, canvas, config["Battery"]["BatteryText"]["Coordinates"],
                                  value=app.get_property("status_battery", 60), posix=posix)

        if "BatteryIcon" in config["Battery"]:
            value = app.get_property("status_battery", 60)
            value = int(config["Battery"]["BatteryIcon"]["ImagesCount"] * (value / 100))
            if value >= config["Battery"]["BatteryIcon"]["ImagesCount"]:
                value = config["Battery"]["BatteryIcon"]["ImagesCount"] - 1
            tools.draw_static_object(
                app, canvas,
                config["Battery"]["BatteryIcon"],
                value=value
            )

        if "Linear" in config["Battery"]:
            index = config["Battery"]["Linear"]["StartImageIndex"]
            segments = config["Battery"]["Linear"]["Segments"]
            progress = app.get_property("status_battery", 60) / 100
            current = int(len(segments) * progress)
            for i in range(current):
                img = app.get_resource(index + i)
                tools.add_to_canvas(canvas, img, (
                    int(segments[i]["X"]),
                    int(segments[i]["Y"])
                ))


def render_time_extra(config, canvas, app):
    loader_miband4.render_analog_clock(app, canvas, config)

    # Alarm
    if "Alarm" in config:
        alarm_enabled = app.get_property("status_alarm", 1)
        if "Text" in config["Alarm"] and alarm_enabled:
            value = round(app.get_property("hours", 12) + app.get_property("minutes", 30) / 100, 2)
            tools.draw_adv_number(app, canvas, config["Alarm"]["Text"], value=value, digits=2,
                                  dot=config["Alarm"]["DelimiterImageIndex"])

        if "ImageOn" in config["Alarm"] and alarm_enabled:
            tools.draw_static_object(app, canvas, config["Alarm"]["ImageOn"])

        if "ImageOff" in config["Alarm"] and not alarm_enabled:
            tools.draw_static_object(app, canvas, config["Alarm"]["ImageOff"])

        if "ImageNoAlarm" in config["Alarm"] and not alarm_enabled:
            tools.draw_static_object(app, canvas, config["Alarm"]["ImageNoAlarm"])


def render_weather(config, canvas, app):
    """
    Render weather modules
    :param config: watchface config
    :param canvas: target canvas
    :param app: generator app context
    :return: void
    """
    if "Weather" in config:
        if "Humidity" in config["Weather"]:
            tools.draw_adv_number(app, canvas, config["Weather"]["Humidity"]["Text"],
                                  value=app.get_property("weather_humidity", 60),
                                  posix=config["Weather"]["Humidity"]["SuffixImageIndex"])

        if "Icon" in config["Weather"]:
            if "CustomIcon" in config["Weather"]["Icon"]:
                tools.draw_static_object(
                    app, canvas,
                    config["Weather"]["Icon"]["CustomIcon"],
                    value=app.get_property("weather_icon", 2)
                )

        if "Wind" in config["Weather"]:
            posix = -1
            wind_language = app.get_property("language", 2)
            if wind_language == 0 and "ImageSuffixCN1" in config["Weather"]["Wind"]:
                posix = config["Weather"]["Wind"]["ImageSuffixCN1"]
            elif wind_language == 1 and "ImageSuffixCN2" in config["Weather"]["Wind"]:
                posix = config["Weather"]["Wind"]["ImageSuffixCN2"]
            elif wind_language == 2 and "ImageSuffixEN" in config["Weather"]["Wind"]:
                posix = config["Weather"]["Wind"]["ImageSuffixEN"]

            tools.draw_adv_number(app, canvas, config["Weather"]["Wind"]["Text"],
                                  value=app.get_property("weather_wind", 25),
                                  posix=posix)

        if "UVIndex" in config["Weather"]:
            tools.draw_adv_number(app, canvas, config["Weather"]["UVIndex"]["UV"]["Text"],
                                  value=app.get_property("weather_uv", 4))

        if "Temperature" in config["Weather"]:
            if "Current" in config["Weather"]["Temperature"] and app.get_property("weather_current", -5) > -100:
                tools.draw_adv_number(app, canvas, config["Weather"]["Temperature"]["Current"]["Number"],
                                      value=app.get_property("weather_current", -5),
                                      posix=config["Weather"]["Temperature"]["Current"]["DegreesImageIndex"],
                                      minus=config["Weather"]["Temperature"]["Current"]["MinusImageIndex"])

            if "Today" in config["Weather"]["Temperature"]:
                if "Separate" in config["Weather"]["Temperature"]["Today"]:
                    c = config["Weather"]["Temperature"]["Today"]["Separate"]

                    if "Day" in config["Weather"]["Temperature"]["Today"]["Separate"] \
                            and app.get_property("weather_day", 10) > -100:
                        tools.draw_adv_number(app, canvas, c["Day"]["Number"],
                                              value=app.get_property("weather_day", 10),
                                              posix=c["Day"]["DegreesImageIndex"], minus=c["Day"]["MinusImageIndex"])

                    if "Night" in config["Weather"]["Temperature"]["Today"]["Separate"] \
                            and app.get_property("weather_night", -15) > -100:
                        tools.draw_adv_number(app, canvas, c["Night"]["Number"],
                                              value=app.get_property("weather_night", -15),
                                              posix=c["Night"]["DegreesImageIndex"],
                                              minus=c["Night"]["MinusImageIndex"])

                if "OneLine" in config["Weather"]["Temperature"]["Today"]:
                    c = config["Weather"]["Temperature"]["Today"]["OneLine"]
                    val_n = app.get_property("weather_night", -15)
                    val_d = app.get_property("weather_day", 10)
                    images = []
                    if val_d < 0:
                        images.append(app.get_resource(c["MinusSignImageIndex"]))
                    images.append(tools.build_number_image(app, c["Number"], val_d, 1))
                    if "DelimiterImageIndex" in c:
                        images.append(app.get_resource(c["DelimiterImageIndex"]))
                    if val_n < 0:
                        images.append(app.get_resource(c["MinusSignImageIndex"]))
                    images.append(tools.build_number_image(app, c["Number"], val_n, 1))

                    img = tools.build_multipart_image(c["Number"], images)
                    xy = tools.calculate_adv_position(c["Number"], img.size, fix_y=True)
                    tools.add_to_canvas(canvas, img, xy)


def render_animation(config, canvas, app):
    # Animation
    if "Other" in config:
        if "Animation" in config["Other"]:
            frame = app.get_property("animation_frame", 0)
            for a in config["Other"]["Animation"]:
                if frame < a["AnimationImages"]["ImagesCount"]:
                    tools.draw_static_object(
                        app, canvas,
                        a["AnimationImages"],
                        value=frame
                    )


def render(app):
    """
    Render app contents
    :param app: target app
    :return: image
    """
    # Spawn canvas, fill with black
    canvas = Image.new("RGBA", (126, 294))
    config = app.config

    render_background(config, canvas, app)
    render_time(config, canvas, app)
    render_activity(config, canvas, app)
    render_date(config, canvas, app)
    render_activity_graph(config, canvas, app)
    render_battery(config, canvas, app)
    render_status_icons(config, canvas, app)
    render_weather(config, canvas, app)
    render_animation(config, canvas, app)
    render_time_extra(config, canvas, app)

    return canvas
