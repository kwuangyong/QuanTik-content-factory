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


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, takeaway_chip="Điều còn đúng hôm nay")
