from __future__ import annotations

import re

from .models import PreviewBlock, PreviewStyle


def plain_markdown_text(text: str) -> str:
    value = text.replace("`", "")
    value = value.replace("**", "").replace("__", "")
    value = value.replace("*", "").replace("_", "")
    return value


def parse_markdown_blocks(markdown: str) -> list[PreviewBlock]:
    items: list[PreviewBlock] = []
    in_code = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            items.append(PreviewBlock(line if line else " ", PreviewStyle.CODE, 14))
            continue
        if not stripped:
            items.append(PreviewBlock("", PreviewStyle.META, 0))
            continue
        if stripped.startswith("#"):
            level = min(2, len(stripped) - len(stripped.lstrip("#")))
            style = PreviewStyle.H1 if level == 1 else PreviewStyle.H2
            items.append(PreviewBlock(stripped[level:].strip(), style, 0))
            continue
        if stripped.startswith(">"):
            items.append(PreviewBlock(stripped[1:].strip(), PreviewStyle.QUOTE, 16))
            continue
        bullet_match = re.match(r"^([-*+])\s+(.*)$", stripped)
        if bullet_match:
            items.append(PreviewBlock("- " + bullet_match.group(2), PreviewStyle.BODY, 12))
            continue
        numbered_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered_match:
            items.append(PreviewBlock(f"{numbered_match.group(1)}. {numbered_match.group(2)}", PreviewStyle.BODY, 12))
            continue
        items.append(PreviewBlock(stripped, PreviewStyle.BODY, 0))
    return items or [PreviewBlock("(empty)", PreviewStyle.META, 0)]
