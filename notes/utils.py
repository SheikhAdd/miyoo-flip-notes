from __future__ import annotations

import re


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


def sanitize_title(title: str) -> str:
    value = re.sub(r'[<>:"/\\\\|?*]+', " ", title)
    value = " ".join(value.split()).strip(" .")
    return value

