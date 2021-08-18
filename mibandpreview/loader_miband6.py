from . import loader_miband5, tools
from PIL import Image


def draw_animation_layers(app, current_frame, img):
    return loader_miband5.draw_animation_layers(app, current_frame, img)


def render(app):
    # Spawn canvas, fill with black
    canvas = Image.new("RGBA", (152, 486))
    config = app.config

    # Use Mi Band 5 render parts :-)
    loader_miband5.render_background(config, canvas, app)
    loader_miband5.render_time(config, canvas, app)
    loader_miband5.render_activity(config, canvas, app)
    loader_miband5.render_date(config, canvas, app)
    loader_miband5.render_activity_graph(config, canvas, app)
    loader_miband5.render_battery(config, canvas, app)
    loader_miband5.render_status_icons(config, canvas, app)
    loader_miband5.render_weather(config, canvas, app)
    loader_miband5.render_animation(config, canvas, app)
    loader_miband5.render_time_extra(config, canvas, app)

    if not app.no_mask:
        m = Image.open(tools.get_root()+"/res/mb6_mask.png").convert("L")
        canvas.putalpha(m)

    return canvas
