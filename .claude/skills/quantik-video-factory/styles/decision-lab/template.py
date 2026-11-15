"""decision-lab (game theory, poker, decision science): setup → intuition → math → simulation → analogy → lesson.

The analogy scene is a mandatory two-column card: where poker/games resemble markets and where the analogy breaks.
"""
import pillar_scenes as P

KIND = "video"
DEFAULTS = {"max_seconds": 75, "kicker": "Ra quyết định"}
ROLES = {"setup": "TRÒ CHƠI", "intuition": "TRỰC GIÁC", "math": "TOÁN", "simulation": "MÔ PHỎNG",
         "analogy": "POKER ↔ THỊ TRƯỜNG", "lesson": "BÀI HỌC"}
VISUALS = {"setup": "statement", "intuition": "statement", "math": "code", "simulation": "chart",
           "analogy": "split", "lesson": "surface"}

ICONS = {"setup": "cards", "intuition": "bulb", "math": "gear", "simulation": "dice", "analogy": "scale", "lesson": "target"}   # pictograms for text-only scenes (pipeline/pictos.py)
SCENES = {"hook": {"cast": [{"who": "rival", "pose": "hold", "face": "focus", "x": 0.24, "flip": False}, {"who": "investor", "pose": "think", "face": "surprised", "x": 0.76, "flip": True}], "props": [{"what": "poker_table"}, {"what": "cards", "x": 0.5, "y": 0.86, "s": 0.5}]}, "setup": {"cast": [{"who": "rival", "pose": "hold", "face": "neutral", "x": 0.24, "flip": False}, {"who": "investor", "pose": "hold", "face": "neutral", "x": 0.76, "flip": True}], "props": [{"what": "poker_table"}, {"what": "cards", "x": 0.5, "y": 0.86, "s": 0.5}]}, "intuition": {"cast": [{"who": "investor", "pose": "think", "face": "focus", "x": 0.3, "flip": False}], "props": [{"what": "cards", "x": 0.72, "y": 0.55}]}, "lesson": {"cast": [{"who": "quant", "pose": "point", "face": "smile", "x": 0.26, "flip": False}], "props": [{"what": "chalkboard", "x": 0.72, "y": 0.45, "s": 0.95}]}}   # characters + props (pipeline/figures.py)


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, icons=ICONS, scenes=SCENES, takeaway_chip="Mang về")
