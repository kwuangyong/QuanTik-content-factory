"""Draw the two bus rides used to introduce variance."""
from math import atan2, cos, degrees, pi, sin

import frames as F
from core import THEME as T
from render import Scene

LANE_W, LANE_H = 876, 382
ROAD_Y = 309
BUS_X = 356
BUMP_CENTERS = (105, 270, 456, 634)
MIDPOINT, FINISH = 290, 800
PALETTES = (
    ("#b3e1d3", "#7fb2a6", "#5f948e", "#e4fff4", "#00796b", "#e9ffdb"),
    ("#fedbb0", "#d5a799", "#b68278", "#fff4db", "#b84330", "#ffe1a1"),
)


def road_height(world_x, row, scale):
    height = ROAD_Y
    for center, change in zip(BUMP_CENTERS, row):
        distance = (world_x - center) / 54
        if abs(distance) < 1:
            height -= 39 * (change / scale) * (1 + cos(pi * distance)) / 2
    return height


def scenery(pen, distance, palette):
    sky, hills, buildings, cloud, _, _ = palette
    pen.ellipse((674, 53, 779, 158), fill=cloud)
    pen.arc((654, 33, 799, 178), 206, 333, fill=cloud, width=2)
    for i in range(4):
        x = (i * 253 + 109 - distance * 0.12) % 1030 - 125
        y = 84 + (i % 3) * 21
        pen.rounded_rectangle((x, y, x + 134, y + 28), 14, fill=cloud)
        pen.ellipse((x + 26, y - 12, x + 76, y + 26), fill=cloud)
    pen.polygon(((0, 237), (116, 168), (235, 212), (369, 146), (531, 217),
                 (723, 157), (876, 212), (876, 336), (0, 336)), fill=hills)
    for i in range(11):
        x = (i * 91 + 12 - distance * 0.32) % 1001 - 86
        y = 184 + (i * 31) % 59
        pen.rounded_rectangle((x, y, x + 68, 313), 5, fill=buildings)
        for floor in range(int(y) + 13, 265, 18):
            for column in (14, 39):
                pen.rectangle((x + column, floor, x + column + 12, floor + 7), fill=sky)
    for i in range(3):
        x = (i * 322 + 158 - distance * 0.69) % 966 - 40
        pen.rounded_rectangle((x + 1, 231, x + 10, 301), 4, fill="#526154")
        for dx, dy, radius in ((-12, 234, 26), (16, 230, 28), (0, 214, 27)):
            pen.ellipse((x + dx - radius, dy - radius, x + dx + radius, dy + radius),
                        fill="#467965" if radius == 27 else "#598d72")
    stop_x = (718 - distance * 0.76) % 1050 - 110
    pen.line((stop_x, 211, stop_x, 298), fill="#354957", width=6)
    pen.rounded_rectangle((stop_x - 16, 197, stop_x + 18, 231), 8, fill="#fff8dc",
                          outline="#354957", width=3)
    pen.rounded_rectangle((stop_x - 9, 204, stop_x + 11, 222), 4, fill="#354957")
    pen.rectangle((stop_x - 6, 208, stop_x + 8, 213), fill="#fff8dc")
    x = (571 - distance * 0.82) % 992 - 58
    stride = 7 * sin(distance / 21)
    pen.line((x, 266, x - stride, 292, x + stride, 299), fill="#303e53", width=7)
    pen.line((x, 265, x + stride + 8, 295), fill="#303e53", width=7)
    pen.rounded_rectangle((x - 9, 246, x + 10, 273), 7, fill="#794b78")
    pen.ellipse((x - 9, 225, x + 9, 246), fill="#a76c4e")


def passenger(pen, x, skin, shirt, shift, driver=False):
    # A jolt moves the head and hands independently from the body.
    head_x, head_y = x + shift, 43 - abs(shift) / 2
    pen.rounded_rectangle((x - 22, 59, x + 23, 88), 13, fill=shirt)
    pen.ellipse((head_x - 15, head_y - 16, head_x + 15, head_y + 16), fill=skin)
    pen.pieslice((head_x - 17, head_y - 17, head_x + 15, head_y + 14), 173, 348, fill="#29313d")
    pen.ellipse((head_x + 5, head_y - 1, head_x + 8, head_y + 2), fill="#29313d")
    pen.arc((head_x + 1, head_y + 2, head_x + 11, head_y + 9), 12, 151, fill="#643e3c", width=2)
    if driver:
        pen.ellipse((x + 16, 59, x + 43, 84), outline="#283746", width=5)
        pen.line((x + 9, 67, x + 28, 67), fill=skin, width=8)
    else:
        cup_x = x + 23 + shift
        pen.polygon(((cup_x, 57), (cup_x + 17, 57), (cup_x + 14, 74), (cup_x + 4, 74)), fill="#ffede2")
        pen.line((cup_x, 57, cup_x + 17, 57), fill="#b95540", width=3)
        if abs(shift) > 5:
            pen.ellipse((cup_x + 10, 46, cup_x + 16, 51), fill="#ae6945")
            pen.ellipse((cup_x + 18, 39, cup_x + 22, 43), fill="#ae6945")


def bus(color, cream, distance, angle, impact):
    sprite = F.Image.new("RGBA", (365, 169))
    pen = F.ImageDraw.Draw(sprite)
    pen.rounded_rectangle((4, 16, 359, 142), 32, fill=color, outline="#243747", width=5)
    pen.rounded_rectangle((23, 22, 341, 94), 19, fill="#c3e7e8", outline="#243747", width=4)
    pen.line((31, 33, 326, 33), fill="#f5ffff", width=3)
    shift = round(10 * impact)
    passenger(pen, 76, "#b87753", "#f4b16f", -shift)
    passenger(pen, 160, "#eab795", "#81649a", shift)
    passenger(pen, 274, "#a66c51", "#3a657c", shift // 2, driver=True)
    for x in (119, 208):
        pen.line((x, 25, x, 93), fill="#273b4b", width=6)
    pen.rectangle((8, 100, 354, 117), fill=cream)
    pen.rounded_rectangle((9, 119, 34, 130), 5, fill="#f68572")
    pen.rounded_rectangle((339, 110, 358, 125), 5, fill="#fff5bd")
    pen.rounded_rectangle((352, 59, 364, 80), 5, fill="#243747")
    for x in (74, 280):
        pen.ellipse((x - 24, 115, x + 24, 163), fill="#283544", outline="#16232b", width=4)
        pen.ellipse((x - 13, 126, x + 13, 152), fill="#a8bac3")
        for spoke in range(5):
            theta = spoke * 2 * pi / 5 + distance / 23
            pen.line((x, 139, x + 10 * cos(theta), 139 + 10 * sin(theta)), fill="#4b6776", width=3)
    return sprite.rotate(angle, resample=F.Image.BICUBIC)


def reaction(pen, impact, palette):
    """Cut in to the passenger and cup as the suspension moves."""
    pen.rounded_rectangle((624, 101, 855, 263), 22, fill="#203944", outline="#f6ebdb", width=3)
    pen.rounded_rectangle((636, 113, 843, 250), 15, fill=palette[1])
    pen.line((642, 124, 837, 124), fill=palette[3], width=4)
    pen.polygon(((637, 221), (690, 173), (734, 223), (843, 180), (843, 247), (637, 247)),
                fill=palette[2])
    shake = round(15 * impact)
    x, y = 711 + shake, 170 - abs(shake) / 2
    pen.rounded_rectangle((658, 201, 766, 247), 19, fill="#715780")
    pen.rounded_rectangle((696, 183, 730, 215), 10, fill="#bc7556")
    pen.ellipse((x - 36, y - 36, x + 36, y + 37), fill="#eab491")
    pen.pieslice((x - 38, y - 40, x + 42, y + 32), 178, 357, fill="#302e3d")
    eye = 8 if abs(shake) >= 5 else 4
    for dx in (-9, 13):
        pen.ellipse((x + dx, y + 1 - eye / 2, x + dx + 6, y + 1 + eye / 2), fill="#302e3d")
    if abs(shake) >= 5:
        pen.ellipse((x + 3, y + 14, x + 16, y + 25), fill="#8b4e4c")
    else:
        pen.arc((x - 4, y + 8, x + 15, y + 23), 10, 165, fill="#8b4e4c", width=3)
    cup_x, cup_y = 788 - shake, 194 - abs(shake)
    pen.line((744, 227, cup_x + 17, cup_y + 22), fill="#eab491", width=13)
    pen.polygon(((cup_x, cup_y), (cup_x + 35, cup_y), (cup_x + 28, cup_y + 37),
                 (cup_x + 7, cup_y + 37)), fill="#fff8e0")
    pen.rounded_rectangle((cup_x - 2, cup_y - 3, cup_x + 37, cup_y + 4), 3, fill="#874c3c")
    if abs(shake) >= 5:
        for dx, dy, radius in ((8, 13, 4), (24, 25, 5), (34, 12, 3)):
            px, py = cup_x + dx - shake / 2, cup_y - dy
            pen.ellipse((px - radius, py - radius, px + radius, py + radius), fill="#874c3c")


def draw_lane(img, top, index, distance, row, scale, active, caption, markers):
    palette = PALETTES[index]
    panel = F.Image.new("RGB", (LANE_W, LANE_H), palette[0])
    pen = F.ImageDraw.Draw(panel)
    scenery(pen, distance, palette)
    points = [(x, road_height(distance + x - BUS_X, row, scale)) for x in range(0, LANE_W + 1, 4)]
    pen.polygon([*points, (LANE_W, LANE_H), (0, LANE_H)], fill="#344955")
    pen.line(points, fill="#f0dfbf", width=5)
    for x in range(-int(distance % 91), LANE_W, 91):
        pen.line((x, 362, x + 45, 362), fill="#b2c3c8", width=3)
    rear = road_height(distance - 102, row, scale)
    front = road_height(distance + 103, row, scale)
    center = road_height(distance, row, scale)
    tilt = degrees(atan2(rear - front, 205))
    impact = max(-1, min(1, tilt / 10 + (ROAD_Y - center) / 73))
    y = round(0.52 * (front + rear) / 2 + 0.48 * center)
    vehicle = bus(palette[4], palette[5], distance, tilt, impact)
    pen.ellipse((BUS_X - 131, y - 4, BUS_X + 137, y + 13), fill="#263b45")
    panel.paste(vehicle, (BUS_X - vehicle.width // 2, y - 156), vehicle)
    if abs(impact) > 0.34:
        for i in range(3):
            px = BUS_X - 174 - i * 20
            py = y - 88 + i * 13
            pen.arc((px - 12, py - 12, px + 13, py + 12), 125, 281, fill=palette[3], width=4)
    if active and not markers:
        reaction(pen, impact, palette)
    mask = F.Image.new("L", panel.size)
    F.ImageDraw.Draw(mask).rounded_rectangle((0, 0, LANE_W - 1, LANE_H - 1), 25, fill=255)
    img.paste(panel, (62, top), mask)
    pen = F.ImageDraw.Draw(img)
    edge = T["accent"] if active else T["border"]
    pen.rounded_rectangle((62, top, 937, top + LANE_H - 1), 25, outline=edge, width=4)
    pen.rounded_rectangle((85, top + 19, 892, top + 84), 18, fill="#192e37")
    F.text_box(img, caption, (104, top + 24, 858, top + 78), size=38,
               color=T["text"], valign="middle", label=f"bus-{index}-label")
    if markers:
        for i, marker in enumerate(markers):
            x = 354 + i * 136
            pen.rounded_rectangle((x, top + 325, x + 123, top + 373), 11, fill="#1b303a")
            F.text_box(img, marker, (x + 4, top + 331, x + 119, top + 370),
                       "mono-bold", 29, T["text"], "center", label=f"bus-{index}-return-{i}")


def scenes(ep, labels, scale):
    rows = (ep["returns_a"], ep["returns_b"])
    headings = (ep["bus_a"], ep["bus_b"])
    question, answer, explain = (ep[key] for key in ("question", "answer", "explain"))
    stages = [
        ("bus-a", ep["say_a"], (0, 0), (FINISH, 0), 0, 1.5),
        ("bus-b-smooth", ep["say_b_smooth"], (FINISH, 0), (FINISH, MIDPOINT), 1, 0),
        ("bus-b-bumps", ep["say_b_bumps"], (FINISH, MIDPOINT), (FINISH, FINISH), 1, 0.95),
        ("guess", ep["hook"], (FINISH, FINISH), (FINISH, FINISH), None, 1.65),
        ("answer", ep["say_answer"], (FINISH, FINISH), (FINISH, FINISH), 1, 0.85),
        ("math", ep["reveal_voice"], (FINISH, FINISH), (FINISH, FINISH), 1, 2.2),
    ]

    def make_scene(stage):
        name, say, start, end, active, min_dur = stage
        reveal = name in ("answer", "math")
        show_math = name == "math"
        footer = explain if show_math else ep["prompt"] if not reveal else ""
        title = answer if reveal else question

        def draw(img, _seconds, progress):
            F.text_box(img, title, (64, 284, 936, 411), "sans-black", 74,
                       T["accent"] if reveal else T["text"], valign="middle", label="title")
            for index, row in enumerate(rows):
                distance = start[index] + (end[index] - start[index]) * progress
                draw_lane(img, 420 + index * 394, index, distance, row, scale, index == active,
                          headings[index], labels[index] if show_math else None)
            if footer:
                F.text_box(img, footer, (68, 1205, 931, 1322), "sans-bold", 37,
                           T["text"] if reveal else T["muted"], "center", "middle", label="explanation")

        texts = [title, *headings, footer]
        if show_math:
            texts.extend(label for row in labels for label in row)
        return Scene(name, say, draw, min_dur, texts)

    return [make_scene(stage) for stage in stages]
