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


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, takeaway_chip="Mang về")
