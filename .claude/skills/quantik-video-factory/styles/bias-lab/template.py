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
SCENES = {"hook": {"cast": [{"who": "investor", "pose": "worried", "face": "worried", "x": 0.32, "flip": False}], "props": [{"what": "phone_down", "x": 0.72, "y": 0.55}]}, "problem": {"cast": [{"who": "investor", "pose": "hold", "face": "worried", "x": 0.32, "flip": False}], "props": [{"what": "phone_down", "x": 0.7, "y": 0.55}]}, "lesson": {"cast": [{"who": "investor", "pose": "think", "face": "focus", "x": 0.3, "flip": False}], "props": [{"what": "newspaper", "x": 0.72, "y": 0.6, "s": 0.9}]}}   # characters + props (pipeline/figures.py)


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, icons=ICONS, scenes=SCENES, takeaway_chip="Mang về")
