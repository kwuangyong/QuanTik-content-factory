"""Draw the price-deviation quiz and its square-tile reveal."""
from math import sin

import frames as F
from core import THEME as T
from render import Scene

INK = "#173039"
TEAL, ORANGE = "#54c6bb", "#ffac76"
TABLE = "#e7d2b3"


def studio(pen, phase):
    pen.rounded_rectangle((62, 462, 937, 1095), 32, fill="#b8d5cb", outline="#54786e", width=3)
    # Window with a skyline behind the desk.
    pen.rounded_rectangle((88, 483, 911, 757), 20, fill="#e6ede0")
    for i, height in enumerate((72, 119, 95, 169, 119, 146, 89, 116, 138, 89, 116)):
        x = 101 + i * 73
        pen.rectangle((x, 754 - height, x + 58, 754), fill="#aac2b4")
        for y in range(769 - height, 742, 23):
            pen.line((x + 10, y, x + 46, y), fill="#d7e1ce", width=4)
    pen.line((500, 486, 500, 757), fill="#8fad9e", width=10)
    pen.line((89, 647, 911, 647), fill="#8fad9e", width=6)
    # Green plant, lamp, and calculator anchor the edges of the shot.
    pen.rounded_rectangle((96, 682, 183, 776), 14, fill="#a55642")
    for dx, rise in ((-34, 58), (-9, 91), (29, 75), (40, 40)):
        top = 681 - rise + 3 * sin(phase + dx)
        pen.line((141, 705, 141 + dx, top + 9), fill="#466c56", width=5)
        pen.ellipse((128 + dx, top - 11, 152 + dx, top + 25), fill="#56886e")
    pen.line((800, 752, 825, 628, 789, 595), fill=INK, width=10)
    pen.polygon(((761, 584), (811, 594), (824, 628), (749, 621)), fill="#eaae6c")
    pen.rounded_rectangle((775, 750, 854, 768), 7, fill=INK)
    pen.rounded_rectangle((63, 751, 936, 1094), 32, fill=TABLE)
    pen.line((78, 765, 920, 765), fill="#f9ebd5", width=5)
    pen.rounded_rectangle((83, 910, 169, 1034), 12, fill="#425e65")
    pen.rounded_rectangle((94, 921, 158, 948), 3, fill="#bce9d6")
    for r in range(3):
        for c in range(3):
            x, y = 96 + c * 22, 960 + r * 20
            pen.rounded_rectangle((x, y, x + 14, y + 12), 3, fill="#e5e7d7")


def analyst(pen, x, y, skin, shirt, side, phase):
    bob = 4 * sin(phase)
    pen.rounded_rectangle((x - 61, y + 39, x + 61, y + 160), 32, fill=shirt)
    pen.rounded_rectangle((x - 17, y + 33 + bob, x + 17, y + 62 + bob), 8, fill=skin)
    pen.ellipse((x - 38, y - 41 + bob, x + 38, y + 45 + bob), fill=skin)
    pen.pieslice((x - 42, y - 47 + bob, x + 42, y + 33 + bob), 175, 367, fill=INK)
    for dx in (-14, 10):
        pen.ellipse((x + dx, y + bob - 2, x + dx + 5, y + bob + 3), fill=INK)
    pen.arc((x - 9, y + 5 + bob, x + 12, y + 20 + bob), 8, 171, fill="#81515a", width=3)
    arm_x, arm_y = x + side * (63 + 20 * sin(phase)), y + 101 + 15 * sin(phase)
    pen.line((x + side * 31, y + 67, arm_x, arm_y), fill=shirt, width=21)
    pen.ellipse((arm_x - 10, arm_y - 10, arm_x + 10, arm_y + 10), fill=skin)


def tile_square(pen, x, y, side, color, progress):
    size, gap = 47, 8
    for row in range(side):
        for col in range(side):
            x0, y0 = x + col * (size + gap), y + row * (size + gap)
            lift = F.ease_out(F.clamp(progress * 1.65 - (row + col) * 0.105))
            pen.rounded_rectangle((x0, y0, x0 + size, y0 + size), 7, outline="#6c8076", width=2)
            if lift > 0:
                y0 -= min(48, y0 - 854) * (1 - lift)
                pen.rounded_rectangle((x0, y0, x0 + size, y0 + size), 7, fill=color, outline=INK, width=2)
                pen.line((x0 + 8, y0 + 8, x0 + 33, y0 + 8), fill="#fbf0d5", width=3)


def scenes(ep):
    small, large = ep["deviations"]
    stages = [
        ("question", ep["hook"], 2.25),
        ("guess", ep["say_options"], 1.7),
        ("answer", ep["say_answer"], 1.25),
        ("math", ep["explain_voice"], 2.1),
    ]

    def make_scene(index, name, say, minimum):
        reveal = index >= 2
        title = ep["answer"] if reveal else ep["question"]
        footers = [ep["left_equation"], ep["right_equation"]] if reveal else ep["choices"]

        def draw(img, t, p):
            F.text_box(img, title, (62, 282, 938, 449), "sans-black", 64,
                       T["accent"] if reveal else T["text"], valign="middle", label="title")
            pen = F.ImageDraw.Draw(img)
            phase = 1.8 * (index + p)
            studio(pen, phase)
            analyst(pen, 272, 638, "#dba680", "#386f6f", 1, phase)
            analyst(pen, 715, 638, "#b87357", "#854e62", -1, phase + 0.45)
            # Two work mats show the magnitude first, then the area.
            for side, point, x, color in ((small, ep["left_label"], 184, TEAL),
                                          (large, ep["right_label"], 540, ORANGE)):
                pen.rounded_rectangle((x, 788, x + 312, 1080), 19, fill="#f4e8d1", outline="#a59272", width=2)
                F.text_box(img, point, (x + 12, 797, x + 300, 851), "sans-bold", 30,
                           INK, "center", "middle", label=f"deviation-{side}")
                if reveal:
                    progress = p if name == "answer" else 1
                    span = 55 * side - 8
                    tile_square(pen, x + (312 - span) // 2, 852 + (220 - span) // 2, side, color, progress)
                else:
                    y = 1004
                    x0 = x + (312 - side * 55) // 2
                    pen.line((x + 27, y, x + 285, y), fill="#82918a", width=3)
                    for col in range(side):
                        block_x = x0 + col * 55
                        bounce = round(5 * sin(phase + col))
                        pen.rounded_rectangle((block_x, y - 49 + bounce, block_x + 47, y - 3 + bounce),
                                              7, fill=color, outline=INK, width=2)
            for i, footer in enumerate(footers):
                x = 75 + i * 444
                box = (x, 1119, x + 406, 1225)
                F.panel(img, box, fill=T["raised"], outline=T["accent"] if reveal and i == 1 else T["border"])
                F.text_box(img, footer, (x + 10, 1130, x + 396, 1215), "sans-bold", 49,
                           T["text"], "center", "middle", label=f"footer-{i}")
            F.text_box(img, ep["explain"] if reveal else ep["baseline"],
                       (68, 1238, 931, 1320), "sans-bold", 35,
                       T["text"] if reveal else T["muted"], "center", "middle", label="context")

        texts = [title, ep["left_label"], ep["right_label"], *footers,
                 ep["explain"] if reveal else ep["baseline"]]
        return Scene(name, say, draw, minimum, texts)

    return [make_scene(i, *stage) for i, stage in enumerate(stages)]
