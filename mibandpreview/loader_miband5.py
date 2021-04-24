from tools import *
from PIL import Image, ImageDraw

def draw_animation_layers(app, current_frame, img):
    config = app.config
    state = [False, False, False, False, False]

    n = 1
    if "Other" in config:
        if "Animation" in config["Other"]:
            for a in config["Other"]["Animation"]:
                if current_frame[n] < a["AnimationImages"]["ImagesCount"]:
                    draw_static_object(app, img, a["AnimationImages"], value=current_frame[n])
                else: state[n] = True
                n += 1

    return (img, state)

def render(app):
    # Spawn canvas, fill with black
    canvas = Image.new("RGBA", (126, 294))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 126, 294), fill="#000000")

    config = app.config

    # Background
    if "Background" in config: 
        if "Image" in config["Background"]:
            draw_static_object(
                app, canvas,
                config["Background"]["Image"]
            )

    # Time
    if "Time" in config:
        if "Hours" in config["Time"]:
            if "Tens" in config["Time"]["Hours"]: 
                draw_static_object(
                    app, canvas,
                    config["Time"]["Hours"]["Tens"],
                    value=app.get_property("hours", 12) // 10
                )

            if "Ones" in config["Time"]["Hours"]: 
                draw_static_object(
                    app, canvas,
                    config["Time"]["Hours"]["Ones"],
                    value=app.get_property("hours", 12) % 10
                )

        if "Minutes" in config["Time"]:
            if "Tens" in config["Time"]["Minutes"]: 
                draw_static_object(
                    app, canvas,
                    config["Time"]["Minutes"]["Tens"],
                    value=app.get_property("minutes", 30) // 10
                )

            if "Ones" in config["Time"]["Minutes"]: 
                draw_static_object(
                    app, canvas,
                    config["Time"]["Minutes"]["Ones"],
                    value=app.get_property("minutes", 30) % 10
                )

        if "DelimiterImage" in config["Time"]: 
            draw_static_object(
                app, canvas, 
                config["Time"]["DelimiterImage"]
            )

        if "TimeZone1" in config["Time"]:
            a = round(app.get_property("hours", 12) + app.get_property("minutes", 30) / 100, 2)
            draw_apos_number(
                app, canvas, 
                config["Time"]["TimeZone1"],
                value=a, dot=config["Time"]["TimeZone1DelimiterImage"],
                digits=2, digits_after_dot=2
            )
        if "TimeZone2" in config["Time"]:
            a = round(app.get_property("hours", 12) + app.get_property("minutes", 30) / 100, 2)
            draw_apos_number(
                app, canvas, 
                config["Time"]["TimeZone2"],
                value=a, dot=config["Time"]["TimeZone1DelimiterImage"],
                digits=2, digits_after_dot=2
            )
    
    if "Activity" in config:
        if "Steps" in config["Activity"]: 
            draw_apos_number(
                app, canvas,
                config["Activity"]["Steps"]["Number"],
                value=app.get_property("steps", 12345)
            )

        if "Pulse" in config["Activity"]: 
            prefix = -1
            if "PrefixImageIndex" in config["Activity"]["Pulse"]:
                prefix = config["Activity"]["Pulse"]["PrefixImageIndex"]

            if app.get_property("heartrate", 120) > 0:
                draw_apos_number(
                    app, canvas,
                    config["Activity"]["Pulse"]["Number"],
                    value=app.get_property("heartrate", 120),
                    prefix=prefix
                )
            elif "NoDataImageIndex" in config["Activity"]["Pulse"]:
                img = app.get_resource(config["Activity"]["Pulse"]["NoDataImageIndex"])
                xy = calculate_apos(config["Activity"]["Pulse"]["Number"], img.size)
                add_to_canvas(canvas, img, xy)

        if "Distance" in config["Activity"]:
            dist = config["Activity"]["Distance"]
            draw_apos_number(
                app, canvas, dist["Number"],
                    value=app.get_property("distance", 14.2),
                dot=dist["DecimalPointImageIndex"],
                posix=dist["KmSuffixImageIndex"]
            )

        if "Calories" in config["Activity"]:
            kcal = config["Activity"]["Calories"]
            posix = -1
            if "SuffixImageIndex" in kcal:
                posix = kcal["SuffixImageIndex"]
            draw_apos_number(
                app, canvas, kcal["Text"],
                value=app.get_property("calories", 500),
                posix=posix
            )

        if "PAI"in config["Activity"]:
            draw_apos_number(
                app, canvas,
                config["Activity"]["PAI"]["Number"],
                value=app.get_property("pai", 88)
            )

    # Date
    twoDMonth = False
    twoDDay = False
    if "Date" in config:
        if "MonthAndDayAndYear" in config["Date"]:
            if "TwoDigitsDay" in config["Date"]["MonthAndDayAndYear"]:
                twoDDay = config["Date"]["MonthAndDayAndYear"]["TwoDigitsDay"]

            if "TwoDigitsMonth" in config["Date"]["MonthAndDayAndYear"]:
                twoDMonth = config["Date"]["MonthAndDayAndYear"]["TwoDigitsMonth"]

            if "OneLine" in config["Date"]["MonthAndDayAndYear"]:
                date = config["Date"]["MonthAndDayAndYear"]["OneLine"]["Number"]
                draw_apos_date(
                    app, canvas, date, 
                    app.get_property("month", 2),
                    app.get_property("day", 15), date["DelimiterImageIndex"], 
                    twoDMonth, twoDDay
                )

            if "Separate" in config["Date"]["MonthAndDayAndYear"]:
                if "Month" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
                    a = draw_apos_number(
                        app, canvas, 
                        config["Date"]["MonthAndDayAndYear"]["Separate"]["Month"],
                        value=app.get_property("month", 2),
                        digits=(2 if twoDMonth else 1)
                    )

                if "MonthsEN" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
                    draw_static_object(
                        app, canvas,
                        config["Date"]["MonthAndDayAndYear"]["Separate"]["MonthsEN"],
                        value=app.get_property("month", 2)
                    )

                if "Day" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
                    draw_apos_number(
                        app, canvas,
                        config["Date"]["MonthAndDayAndYear"]["Separate"]["Day"],
                        value=app.get_property("day", 15),
                        digits=(2 if twoDDay else 1)
                    )

        if "ENWeekDays" in config["Date"] and app.get_property("lang_weekday", 2) == 2:
            draw_static_object(
                app, canvas, config["Date"]["ENWeekDays"],
                value=app.get_property("weekday", 3)-1
            )

        if "CN1WeekDays" in config["Date"] and app.get_property("lang_weekday", 2) == 0:
            draw_static_object(
                app, canvas, config["Date"]["CN1WeekDays"],
                value=app.get_property("weekday", 3)-1
            )

        if "CN2WeekDays" in config["Date"] and app.get_property("lang_weekday", 2) == 1:
            draw_static_object(
                app, canvas, config["Date"]["CN2WeekDays"],
                value=app.get_property("weekday", 3)-1
            )

        if "DayAmPm" in config["Date"] and not app.get_property("24h", 0) == 1:
            apm = config["Date"]["DayAmPm"]
            val = app.get_property("ampm", 0)
            lang = app.get_property("lang_ampm", 0)
            if val == 1 and lang == 1: index = apm["ImageIndexPMCN"]
            elif val == 0 and lang == 1: index = apm["ImageIndexAMCN"]
            elif val == 1 and lang == 0: index = apm["ImageIndexPMEN"]
            elif val == 0 and lang == 0: index = apm["ImageIndexAMEN"]
            add_to_canvas(
                canvas, 
                app.get_resource(index), 
                (int(apm["X"]), int(apm["Y"]))
            )

    # Indicators
    if "StepsProgress" in config:
        steps = app.get_property("steps", 6000)
        target = app.get_property("target_steps", 9000)
        if "Linear" in config["StepsProgress"]:
            draw_steps_bar(
                app, canvas, 
                config["StepsProgress"]["Linear"],
                min(1, steps / target)
            )
        if "LineScale" in config["StepsProgress"]:
            curSegment = int(config["StepsProgress"]["LineScale"]["ImagesCount"] * min(1, steps / target))
            if curSegment >= config["StepsProgress"]["LineScale"]["ImagesCount"]:
                curSegment = config["StepsProgress"]["LineScale"]["ImagesCount"]-1
            draw_static_object(
                app, canvas,
                config["StepsProgress"]["LineScale"],
                value=curSegment
            )

    if "Heart" in config:
        if "Scale" in config["Heart"]:
            index = config["Heart"]["Scale"]["StartImageIndex"]
            segments = config["Heart"]["Scale"]["Segments"]
            value = app.get_property("heartrate", 200)
            i = int(max(0,min(1, value/202)*len(segments)-1))
            if i <= len(segments):
                img = app.get_resource(index+i)
                xy = (int(segments[i]["X"]), int(segments[i]["Y"]))
                add_to_canvas(canvas, img, xy)

    # Status
    if "Status" in config:
        if "DoNotDisturb" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["DoNotDisturb"] and app.get_property("status_mute", 1):
                add_to_canvas(
                    canvas, 
                    app.get_resource(config["Status"]["DoNotDisturb"]["ImageIndexOn"]),
                    (config["Status"]["DoNotDisturb"]["Coordinates"]["X"],
                    config["Status"]["DoNotDisturb"]["Coordinates"]["Y"])
                )

            if "ImageIndexOff" in config["Status"]["DoNotDisturb"] and not app.get_property("status_mute", 1):
                add_to_canvas(
                    canvas, 
                    app.get_resource(config["Status"]["DoNotDisturb"]["ImageIndexOff"]),
                    (config["Status"]["DoNotDisturb"]["Coordinates"]["X"],
                    config["Status"]["DoNotDisturb"]["Coordinates"]["Y"])
                )

        if "Lock" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["Lock"] and not app.get_property("status_lock", 1):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Lock"]["ImageIndexOn"]),
                    (config["Status"]["Lock"]["Coordinates"]["X"],
                    config["Status"]["Lock"]["Coordinates"]["Y"])
                )

            if "ImageIndexOff" in config["Status"]["Lock"] and app.get_property("status_lock", 1):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Lock"]["ImageIndexOff"]),
                    (config["Status"]["Lock"]["Coordinates"]["X"],
                    config["Status"]["Lock"]["Coordinates"]["Y"])
                )

        if "Bluetooth" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["Bluetooth"] and app.get_property("status_bluetooth", 0):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Bluetooth"]["ImageIndexOn"]),
                    (config["Status"]["Bluetooth"]["Coordinates"]["X"],
                    config["Status"]["Bluetooth"]["Coordinates"]["Y"])
                )

            if "ImageIndexOff" in config["Status"]["Bluetooth"] and not app.get_property("status_bluetooth", 0):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Bluetooth"]["ImageIndexOff"]),
                    (config["Status"]["Bluetooth"]["Coordinates"]["X"],
                    config["Status"]["Bluetooth"]["Coordinates"]["Y"])
                )

    if "Battery" in config:
        if "BatteryText" in config["Battery"]:
            posix = -1
            if "SuffixImageIndex" in config["Battery"]["BatteryText"]: 
                posix = config["Battery"]["BatteryText"]["SuffixImageIndex"]
            draw_apos_number(
                app, canvas, 
                config["Battery"]["BatteryText"]["Coordinates"],
                value=app.get_property("status_battery", 60),
                posix=posix
            )

        if "BatteryIcon" in config["Battery"]:
            value = app.get_property("status_battery", 60)
            value = int(config["Battery"]["BatteryIcon"]["ImagesCount"]*(value/100))
            if value >= config["Battery"]["BatteryIcon"]["ImagesCount"]:
                value=config["Battery"]["BatteryIcon"]["ImagesCount"]-1
            draw_static_object(
                app, canvas, 
                config["Battery"]["BatteryIcon"],
                value=value
            )
        
        if "Linear" in config["Battery"]:
            index = config["Battery"]["Linear"]["StartImageIndex"]
            segments = config["Battery"]["Linear"]["Segments"]
            progress = app.get_property("status_battery", 60)/100
            curSegment = int(len(segments) * progress)
            for i in range(curSegment):
                img = app.get_resource(index+i)
                add_to_canvas(canvas, img, (
                    int(segments[i]["X"]),
                    int(segments[i]["Y"])
                ))

    # Analog clock
    if "AnalogDialFace" in config:
        hours = app.get_property("hours", 12)
        minutes = app.get_property("minutes", 30)
        seconds = app.get_property("seconds", 40)
        if "Hours" in config["AnalogDialFace"]:
            draw_analog_dial(
                app, canvas,
                config["AnalogDialFace"]["Hours"],
                30*( hours + minutes /60 )
            )

            if "CenterImage" in config["AnalogDialFace"]["Hours"]:
                draw_static_object(
                    app, canvas, 
                    config["AnalogDialFace"]["Hours"]["CenterImage"]
                )

        if "Minutes" in config["AnalogDialFace"]:
            draw_analog_dial(
                app, canvas,
                config["AnalogDialFace"]["Minutes"],
                30*minutes
            )

            if "CenterImage" in config["AnalogDialFace"]["Minutes"]:
                draw_static_object(
                    app, canvas, 
                    config["AnalogDialFace"]["Minutes"]["CenterImage"]
                )

        if "Seconds" in config["AnalogDialFace"]:
            draw_analog_dial(
                app, canvas, 
                config["AnalogDialFace"]["Seconds"], 
                30*seconds
            )

            if "CenterImage" in config["AnalogDialFace"]["Seconds"]:
                draw_static_object(
                    app, canvas, 
                    config["AnalogDialFace"]["Seconds"]["CenterImage"]
                )

    # Alarm
    if "Alarm" in config:
        alarm_enabled = app.get_property("status_alarm", 1)
        if "Text" in config["Alarm"] and alarm_enabled:
            value = round(app.get_property("hours", 12)+app.get_property("minutes", 30)/100, 2)
            draw_apos_number(
                app, canvas, 
                config["Alarm"]["Text"],
                value=value,
                dot=config["Alarm"]["DelimiterImageIndex"],
                digits=2, digits_after_dot=2
            )
 
        if "ImageOn" in config["Alarm"] and alarm_enabled:
            draw_static_object(app, canvas, config["Alarm"]["ImageOn"])

        if "ImageOff" in config["Alarm"] and not alarm_enabled:
            draw_static_object(app, canvas, config["Alarm"]["ImageOff"])

        if "ImageNoAlarm" in config["Alarm"] and not alarm_enabled:
            draw_static_object(app, canvas, config["Alarm"]["ImageNoAlarm"])

    # Weather
    if "Weather" in config:
        if "Humidity" in config["Weather"]:
            draw_apos_number(
                app, canvas,
                config["Weather"]["Humidity"]["Text"],
                value=app.get_property("weather_humidity", 60),
                posix=config["Weather"]["Humidity"]["SuffixImageIndex"]
            )

        if "Icon" in config["Weather"]:
            if "CustomIcon" in config["Weather"]["Icon"]:
                draw_static_object(
                    app, canvas, 
                    config["Weather"]["Icon"]["CustomIcon"],
                    value=app.get_property("weather_icon", 2)
                )

        if "Temperature" in config["Weather"]:
            if "Current" in config["Weather"]["Temperature"]:
                draw_apos_number(
                    app, canvas, 
                    config["Weather"]["Temperature"]["Current"]["Number"],
                    value=app.get_property("weather_current", -5),
                    posix=config["Weather"]["Temperature"]["Current"]["DegreesImageIndex"],
                    minus=config["Weather"]["Temperature"]["Current"]["MinusImageIndex"]
                )

            if "Today" in config["Weather"]["Temperature"]:
                if "Separate" in config["Weather"]["Temperature"]["Today"]:
                    c = config["Weather"]["Temperature"]["Today"]["Separate"]

                    if "Day" in config["Weather"]["Temperature"]["Today"]["Separate"]:
                        draw_apos_number(
                            app, canvas,
                            c["Day"]["Number"],
                            value=app.get_property("wather_day", 10),
                            posix=c["Day"]["DegreesImageIndex"],
                            minus=c["Day"]["MinusImageIndex"]
                        )

                    if "Night" in config["Weather"]["Temperature"]["Today"]["Separate"]:
                        draw_apos_number(
                            app, canvas,
                            c["Night"]["Number"],
                            value=app.get_property("wather_night", -15),
                            posix=c["Night"]["DegreesImageIndex"],
                            minus=c["Night"]["MinusImageIndex"]
                        )

                if "OneLine" in config["Weather"]["Temperature"]["Today"]:
                    c = config["Weather"]["Temperature"]["Today"]["OneLine"]
                    val_n = app.get_property("wather_night", -15)
                    val_d = app.get_property("wather_day", 10)
                    images = []
                    if val_d < 0:
                        images.append(app.get_resource(c["MinusSignImageIndex"]))
                    images.append(build_number_image(app, c["Number"], val_d, 1))
                    if "DelimiterImageIndex" in c:
                        images.append(app.get_resource(c["DelimiterImageIndex"]))
                    if val_n < 0:
                        images.append(app.get_resource(c["MinusSignImageIndex"]))
                    images.append(build_number_image(app, c["Number"], val_n, 1))
                    
                    img = build_multipart_image(c["Number"], images)
                    xy = calculate_apos(c["Number"], img.size)
                    add_to_canvas(canvas, img, xy)

    # Other
    if "Other" in config:
        if "Animation" in config["Other"]:
            frame = app.get_property("animation_frame", 0)
            for a in config["Other"]["Animation"]:
                if frame < a["AnimationImages"]["ImagesCount"]:
                    draw_static_object(
                        app, canvas, 
                        a["AnimationImages"],
                        value=frame
                    )

    return canvas
