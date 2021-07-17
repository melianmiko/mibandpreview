import math
import os
from PIL import Image, ImageDraw


def add_to_canvas(target, img, xy):
    x, y = xy
    sx = sy = 0
    if x < 0:
        sx = -x
        x = 0
    if y < 0:
        sy = -y
        y = 0
    target.alpha_composite(img, (x, y), (sx, sy))


def draw_static_object(app, canvas, obj, value=0):
    image_index = int(obj["ImageIndex"])
    image_id = image_index + value
    img = app.get_resource(image_id)
    add_to_canvas(canvas, img, (obj["X"], obj["Y"]))
    return (
        int(obj["X"]), int(obj["Y"]),
        int(obj["X"]) + img.size[0], int(obj["Y"]) + img.size[1]
    )


def draw_adv_number(app, canvas, obj, value=0, digits=1, dot=-1, posix=-1, prefix=-1, minus=-1):
    images = []
    if prefix > -1:
        images.append(app.get_resource(prefix))

    if value < 0:
        value = -value
        if minus > -1:
            images.append(app.get_resource(minus))

    if isinstance(value, int):
        images += split_number_to_images(app, obj, value, digits)
    else:
        images += split_number_to_images(app, obj, math.floor(value), digits)
        if dot > -1:
            dot_img = app.get_resource(dot)
            device = app.get_property("device", "miband4")
            if device == "miband5" or device == "miband6":
                if dot_img.size[1] < images[0].size[1]:
                    new_image = Image.new("RGBA", (dot_img.size[0], images[0].size[1]))
                    new_image.paste(dot_img, (0, images[0].size[1] - dot_img.size[1]))
                    dot_img = new_image
            images.append(dot_img)
        after_dot = str(value).split(".")[1]
        after_dot_len = max(digits, len(after_dot))
        images += split_number_to_images(app, obj, int(after_dot), after_dot_len)

    if posix > -1:
        images.append(app.get_resource(posix))

    align = decode_align(obj["Alignment"])
    x1 = int(obj["TopLeftX"])
    x2 = int(obj["BottomRightX"])
    y1 = int(obj["TopLeftY"])
    y2 = int(obj["BottomRightY"])

    ox = 0
    oy = 0

    if "Spacing" in obj:
        ox = obj["Spacing"]
    elif "SpacingX" in obj:
        ox = obj["SpacingX"]

    if "SpacingY" in obj:
        oy = obj["SpacingY"]

    full_width = ox*len(images)
    max_height = 0
    for a in images:
        full_width += a.size[0]
        max_height = max(max_height, a.size[1])

    # Align (horizontal)
    if align[0] == "end":
        x = max(x2-full_width, x1)
    elif align[0] == "center":
        x = round(max(x1, (x2-full_width) / 2))
    else:
        x = x1

    # Align (vertical)
    if align[1] == "end":
        y = max(y2-max_height, y1)
    elif align[1] == "center":
        y = round(max(y1, (y2-max_height)/2))
    else:
        y = y1

    for i in images:
        delta = 0
        add_to_canvas(canvas, i, (x, y+delta))
        x += i.size[0] + ox
        y += oy


def draw_date(app, canvas, obj, month, day, split, month_digits, day_digits, year=-1):
    images = []
    if year > -1:
        images += split_number_to_images(app, obj, year, digits=4)
        if split > -1:
            images.append(app.get_resource(split))

    images += split_number_to_images(app, obj, month, digits=(2 if month_digits else 1))
    if split > -1:
        images.append(app.get_resource(split))

    images += split_number_to_images(app, obj, day, digits=(2 if day_digits else 1))

    i = build_multipart_image(obj, images)
    xy = calculate_adv_position(obj, i.size, fix_y=True)
    add_to_canvas(canvas, i, xy)

    return (
        xy[0], xy[1],
        xy[0] + i.size[0], xy[1] + i.size[1]
    )


def draw_steps_bar(app, canvas, config, progress):
    index = config["StartImageIndex"]
    segments = config["Segments"]
    curSegment = int(len(segments) * progress)
    x = y = 1024
    x2 = y2 = 0
    for i in range(curSegment):
        img = app.get_resource(index + i)
        xy = (int(segments[i]["X"]), int(segments[i]["Y"]))
        add_to_canvas(canvas, img, xy)
        x = min(x, xy[0])
        y = min(y, xy[1])
        x2 = max(x2, xy[0] + img.size[0])
        y2 = max(x2, xy[1] + img.size[1])
    return x, y, x2, y2


def draw_analog_dial(canvas, obj, angle):
    cx = obj["Center"]["X"]
    cy = obj["Center"]["Y"]
    color = obj["Color"].replace("0x", "#")
    border = obj["OnlyBorder"]
    shape = obj["Shape"]
    draw = ImageDraw.Draw(canvas)
    angle = (angle - 360 if angle > 360 else angle)

    points = []
    for dot in shape:
        x = cx + (dot["X"] * radian_sin(angle)) + (dot["Y"] * radian_sin(angle + 90))
        y = cy - (dot["X"] * radian_cos(angle)) - (dot["Y"] * radian_cos(angle + 90))

        points.append((x, y))

    if border:
        draw.polygon(points, outline=color)
    else:
        draw.polygon(points, outline=color, fill=color)


# ---------------------------------------------------------------------------


def split_number_to_images(app, obj, value, digits):
    index_start = obj["ImageIndex"]
    num_images = app.get_resources_set(index_start, obj["ImagesCount"])

    # Split number to litters
    images = []
    if value == 0:
        images.append(num_images[0])
    else:
        while value > 0:
            images.append(num_images[value % 10])
            value = value // 10
    while len(images) < digits:
        images.append(num_images[0])
    images = images[::-1]
    return images


def build_number_image(app, obj, value, digits):
    return build_multipart_image(obj, split_number_to_images(app, obj, value, digits))


def build_multipart_image(data, images, fix_height=False):
    # Load spacings
    spacing_x = 0
    spacing_y = 0
    if "SpacingY" in data:
        spacing_y = data["SpacingY"]

    if "Spacing" in data:
        spacing_x = data["Spacing"]
    elif "SpacingX" in data:
        spacing_x = data["SpacingX"]

    # Calculate width/height
    w = h = 0
    mh = 0
    for n in images:
        w += n.size[0] + abs(spacing_x)
        h = max(h, n.size[1]) + abs(spacing_y)
        mh = max(mh, n.size[1])

    w = max(0, w)
    h = max(0, h)

    # Build image
    img = Image.new("RGBA", (w, h))
    x = 0
    y = 0 if spacing_y >= 0 else -spacing_y * (len(images))
    for n in images:
        offset = 0
        if n.size[1] < mh and fix_height:
            offset = mh - n.size[1]
        add_to_canvas(img, n, (x, y + offset))
        x += n.size[0] + spacing_x
        y += spacing_y

    return img


def decode_align(align):
    if align == "TopLeft" or align == "Left":
        return ["start", "start"]
    if align == "TopRight" or align == "Right":
        return ["end", "start"]
    if align == "TopCenter":
        return ["center", "start"]
    if align == "BottomLeft":
        return ["start", "end"]
    if align == "BottomRight":
        return ["end", "end"]
    if align == "BottomCenter":
        return ["center", "end"]
    if align == "CenterLeft":
        return ["start", "center"]
    if align == "CenterRight":
        return ["end", "center"]
    if align == "Center":
        return ["center", "center"]
    raise Exception("Undefined align mode "+align)


def calculate_adv_position(data, size, fix_y=False):
    x1 = int(data["TopLeftX"])
    x2 = int(data["BottomRightX"])
    y1 = int(data["TopLeftY"])
    y2 = int(data["BottomRightY"])

    w = size[0]
    h = size[1]

    y_offset = 0
    if "SpacingY" in data and fix_y:
        y_offset = -abs(data["SpacingY"])

    rp = x2 - w if x2 - w >= x1 else x1
    bp = y2 - h if y2 - h >= y1 else y1
    cx = int(max(x1/2 + x2/2 - w/2, x1))
    cy = int(max(y1/2 + y2/2 - h/2, y1))

    align = data["Alignment"]
    if align == "TopLeft" or align == "Top" or align == "Left":
        return [x1, y1 + y_offset]
    elif align == "BottomRight":
        return [rp, bp + y_offset]
    elif align == "BottomLeft" or align == "Bottom":
        return [x1, bp + y_offset]
    elif align == "TopRight" or align == "Right":
        return [rp, y1 + y_offset]
    elif align == "TopCenter" or align == "HCenter":
        return [cx, y1 + y_offset]
    elif align == "BottomCenter":
        return [cx, bp + y_offset]
    elif align == "CenterLeft" or align == "VCenter":
        return [x1, cy + y_offset]
    elif align == "CenterRight":
        return [rp, cy + y_offset]
    elif align == "Center":
        return [cx, cy + y_offset]
    else:
        print("Align mode unsupported!!!!!")
        return [x1, y1]


def radian_sin(angle):
    return math.sin(math.radians(angle))


def radian_cos(angle):
    return math.cos(math.radians(angle))


def get_root():
    return os.path.dirname(os.path.abspath(__file__))
