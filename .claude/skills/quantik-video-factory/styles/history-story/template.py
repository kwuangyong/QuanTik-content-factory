"""history-story (quant history): hook → context → conflict → breakthrough → consequences → quant lesson.

A timeline grows through the episode; every event dot is coloured by its claim status (tư liệu / lời tự kể /
giai thoại / còn tranh cãi), and each scene names its sources at the bottom. The breakthrough can show the linked
model running (e.g. Thorp → Kelly) so the "lesson" is computed, not asserted.
"""
import pillar_scenes as P

KIND = "video"
DEFAULTS = {"max_seconds": 80, "kicker": "Lịch sử quant"}
ROLES = {"context": "BỐI CẢNH", "conflict": "BÀI TOÁN", "breakthrough": "ĐỘT PHÁ", "consequences": "HỆ QUẢ",
         "lesson": "BÀI HỌC QUANT"}
VISUALS = {"context": "timeline", "conflict": "statement", "breakthrough": "chart", "consequences": "timeline",
           "lesson": "terminal"}

ICONS = {"context": "book", "conflict": "target", "breakthrough": "bulb", "consequences": "hourglass", "lesson": "check"}   # pictograms for text-only scenes (pipeline/pictos.py)
SCENES = {"hook": {"cast": [{"who": "professor", "pose": "point", "face": "smile", "x": 0.3, "flip": False}], "props": [{"what": "chalkboard", "x": 0.72, "y": 0.45, "s": 0.95}]}, "conflict": {"cast": [{"who": "professor", "pose": "think", "face": "focus", "x": 0.28, "flip": False}], "props": [{"what": "cards", "x": 0.66, "y": 0.62}, {"what": "chips", "x": 0.86, "y": 0.78, "s": 0.8}]}}   # characters + props (pipeline/figures.py)


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, icons=ICONS, scenes=SCENES, takeaway_chip="Điều còn đúng hôm nay")
