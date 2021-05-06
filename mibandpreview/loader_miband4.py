from tools import *
from PIL import Image, ImageDraw

def draw_animation_layers(app, current_frame, img):
    config = app.config
    state = [False, False]

    if "Other" in config:
        if "Animation" in config["Other"]:
            if current_frame[0] < config["Other"]["Animation"]["AnimationImage"]["ImagesCount"]:
                draw_static_object(
                    app, canvas, 
                    config["Other"]["Animation"]["AnimationImage"],
                    value=current_frame[0]
                    )
            else: state[1] = True

    return (img, state)

def render(app):
    # Spawn canvas, fill with black
    canvas = Image.new("RGBA", (120, 240))
    draw = ImageDraw.Draw(canvas)
    #draw.rectangle((0, 0, 120, 240), fill="#000000")

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
    
    # Activity
    if "Activity" in config:
        if "Steps" in config["Activity"]: 
            draw_apos_number(
                app, canvas,
                config["Activity"]["Steps"]["Number"],
                value=app.get_property("steps", 12345)
            )

        if "Pulse" in config["Activity"]: 
            draw_apos_number(
                app, canvas,
                config["Activity"]["Pulse"]["Number"],
                value=app.get_property("heartrate", 120)
            )

        if "Distance" in config["Activity"]:
            dist = config["Activity"]["Distance"]
            draw_apos_number(
                app, canvas, dist["Number"],
                    value=app.get_property("distance", 14.25),
                dot=dist["DecimalPointImageIndex"],
                posix=dist["SuffixImageIndex"]
            )

        if "Calories" in config["Activity"]:
            kcal = config["Activity"]["Calories"]
            draw_apos_number(
                app, canvas, kcal["Number"],
                value=app.get_property("calories", 500),
                posix=kcal["SuffixImageIndex"]
            )
    
    # Date
    twoDMonth = False
    twoDDay = False
    if "Date" in config:
        if "MonthAndDay" in config["Date"]:
            if "TwoDigitsDay" in config["Date"]["MonthAndDay"]:
                twoDDay = config["Date"]["MonthAndDay"]["TwoDigitsDay"]

            if "TwoDigitsMonth" in config["Date"]["MonthAndDay"]:
                twoDMonth = config["Date"]["MonthAndDay"]["TwoDigitsMonth"]

            if "OneLine" in config["Date"]["MonthAndDay"]:
                date = config["Date"]["MonthAndDay"]["OneLine"]["Number"]
                dot = -1
                if "DelimiterImageIndex" in date:
                    dot = date["DelimiterImageIndex"]

                draw_apos_date(
                    app, canvas, date, 
                    app.get_property("month", 2),
                    app.get_property("day", 15), dot,
                    twoDMonth, twoDDay
                )

            if "Separate" in config["Date"]["MonthAndDay"]:
                if "Month" in config["Date"]["MonthAndDay"]["Separate"]:
                    a = draw_apos_number(
                        app, canvas, config["Date"]["MonthAndDay"]["Separate"]["Month"],
                            value=app.get_property("month", 12),
                        digits=(2 if twoDMonth else 1))
                if "Day" in config["Date"]["MonthAndDay"]["Separate"]:
                    draw_apos_number(
                        app, canvas, config["Date"]["MonthAndDay"]["Separate"]["Day"],
                        value=app.get_property("day", 15),
                        digits=(2 if twoDDay else 1))

        if "WeekDay" in config["Date"]:
            draw_static_object(
                app, canvas, config["Date"]["WeekDay"],
                value=app.get_property("weekday", 3)-1+app.get_property("lang_weekday", 2)*7
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
        if "Linear" in config["StepsProgress"]:
            steps = app.get_property("steps", 6000)
            target = app.get_property("target_steps", 9000)
            draw_steps_bar(
                app, canvas, 
                config["StepsProgress"]["Linear"],
                min(1, steps / target)
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
            if "ImageIndexOn" in config["Status"]["Lock"] and app.get_property("status_lock", 1):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Lock"]["ImageIndexOn"]),
                    (config["Status"]["Lock"]["Coordinates"]["X"],
                    config["Status"]["Lock"]["Coordinates"]["Y"])
                )

            if "ImageIndexOff" in config["Status"]["Lock"] and not app.get_property("status_lock", 1):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Lock"]["ImageIndexOff"]),
                    (config["Status"]["Lock"]["Coordinates"]["X"],
                    config["Status"]["Lock"]["Coordinates"]["Y"])
                )

        if "Bluetooth" in config["Status"]:
            if "ImageIndexOn" in config["Status"]["Bluetooth"] and app.get_property("status_bluetooth", 1):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Bluetooth"]["ImageIndexOn"]),
                    (config["Status"]["Bluetooth"]["Coordinates"]["X"],
                    config["Status"]["Bluetooth"]["Coordinates"]["Y"])
                )

            if "ImageIndexOff" in config["Status"]["Bluetooth"] and not app.get_property("status_bluetooth", 1):
                add_to_canvas(
                    canvas,
                    app.get_resource(config["Status"]["Bluetooth"]["ImageIndexOff"]),
                    (config["Status"]["Bluetooth"]["Coordinates"]["X"],
                    config["Status"]["Bluetooth"]["Coordinates"]["Y"])
                )

        if "Battery" in config["Status"]:
            if "Text" in config["Status"]["Battery"]:
                draw_apos_number(
                    app, canvas, 
                    config["Status"]["Battery"]["Text"],
                    value=app.get_property("status_battery", 60)
                )

            if "Icon" in config["Status"]["Battery"]:
                value = app.get_property("status_battery", 60)
                value = int(config["Status"]["Battery"]["Icon"]["ImagesCount"]*(value/100))
                if value >= config["Status"]["Battery"]["Icon"]["ImagesCount"]:
                    value=config["Status"]["Battery"]["Icon"]["ImagesCount"]-1
                draw_static_object(
                    app, canvas, 
                    config["Status"]["Battery"]["Icon"],
                    value=value
                )

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
    
    # Other
    if "Other" in config:
        if "Animation" in config["Other"]:
            frame = app.get_property("animation_frame", 0)
            if frame < config["Other"]["Animation"]["AnimationImage"]["ImagesCount"]:
                draw_static_object(
                    app, canvas, 
                    config["Other"]["Animation"]["AnimationImage"],
                    value=frame
                )

    return canvas
