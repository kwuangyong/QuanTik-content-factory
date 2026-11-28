"""Kiểm tra theo nguyên tắc TikTok (xem mục "Checklist TikTok" trong brand/compliance.md).

Chặn (fail): mời vào nhóm Zalo/Telegram/Discord, số điện thoại, link rút gọn, lời mời "nhận tín hiệu"/"room VIP".
Cảnh báo (người duyệt xử lý khi đăng): bật nhãn AI, không bật Branded Content, nhạc Commercial Music Library.

Usage: python check_platform.py --text "câu cần kiểm tra"
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata

BLOCK = [
    (r"\bzalo\b|\btelegram\b|\bt\.me/|\bdiscord\b|\bwhatsapp\b", "mời sang app nhắn tin (TikTok hạn chế, dễ bị coi là lừa đảo đầu tư)"),
    (r"(?<!\d)(?:\+?84|0)(?:[\s.]?\d){9}(?!\d)", "số điện thoại"),
    (r"\bbit\.ly\b|\btinyurl\b|\bshorturl\b", "link rút gọn"),
    (r"nhận tín hiệu|room vip|nhóm vip|group vip|tín hiệu miễn phí|inbox (?:để|nhận)|ib (?:để|nhận)", "mời nhận tín hiệu/nhóm kín"),
    (r"follow (?:để|nhận)|like (?:để|nhận)|share (?:để|nhận)", "đổi tương tác lấy quà (engagement bait)"),
]

WARN = [
    "Bật nhãn “Nội dung do AI tạo” khi đăng (giọng đọc TTS, hình dựng bằng code).",
    "Không bật “Nội dung thương hiệu” cho video nói về đầu tư/dịch vụ tài chính.",
    "Nhạc: chỉ dùng pad của pipeline hoặc Commercial Music Library.",
]


def check(texts, ep=None):
    issues = []
    for text in texts:
        t = unicodedata.normalize("NFC", text or "").lower()
        for pat, why in BLOCK:
            m = re.search(pat, t)
            if m:
                issues.append(f"{why}: “{m.group(0)}”")
    if ep is not None and len(ep.get("hashtags", [])) > 6:
        issues.append(f"{len(ep['hashtags'])} hashtag: TikTok nên 3–6 hashtag liên quan")
    return {"fail": bool(issues), "issues": sorted(set(issues)), "warnings": WARN}


if __name__ == "__main__":
    res = check([" ".join(sys.argv[2:])] if sys.argv[1:2] == ["--text"] else sys.stdin.read().splitlines())
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(1 if res["fail"] else 0)
