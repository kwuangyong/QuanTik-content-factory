"""bias-lab (behavioral finance): problem → mechanism → evidence → implication → lesson → quant perspective.

Tone: a lab notebook on a familiar mistake. The evidence scene is a study card with the citation; the implication
is the computed model (value function, simulation), never a motivational line.
"""
import pillar_scenes as P

KIND = "video"
DEFAULTS = {"max_seconds": 75, "kicker": "Tâm lý nhà đầu tư"}
ROLES = {"problem": "VẤN ĐỀ", "mechanism": "CƠ CHẾ", "evidence": "BẰNG CHỨNG", "implication": "HỆ QUẢ",
         "lesson": "BÀI HỌC", "quant": "GÓC NHÌN QUANT"}
VISUALS = {"problem": "statement", "mechanism": "chart", "evidence": "citation", "implication": "surface",
           "lesson": "statement", "quant": "terminal"}

ICONS = {"problem": "warning", "mechanism": "gear", "evidence": "book", "implication": "coins", "lesson": "bulb", "quant": "chart_up"}   # pictograms for text-only scenes (pipeline/pictos.py)


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, icons=ICONS, takeaway_chip="Mang về")
