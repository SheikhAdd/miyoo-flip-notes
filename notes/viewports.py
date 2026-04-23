from __future__ import annotations

from typing import Callable


def clamp_scroll(current_scroll: int, cursor_line: int, total_lines: int, visible_rows: int, follow_cursor: bool) -> int:
    if total_lines <= 0:
        return 0

    visible_rows = max(1, visible_rows)
    next_scroll = current_scroll
    if follow_cursor:
        if cursor_line < next_scroll:
            next_scroll = cursor_line
        elif cursor_line >= next_scroll + visible_rows:
            next_scroll = cursor_line - visible_rows + 1

    max_scroll = max(0, total_lines - visible_rows)
    return max(0, min(next_scroll, max_scroll))


def fit_cursor_window(
    text: str,
    cursor: int,
    max_width: int,
    measure: Callable[[str], int],
) -> tuple[str, int]:
    if max_width <= 0:
        return ("", 0)

    cursor = max(0, min(cursor, len(text)))
    start = cursor
    while start > 0 and measure(text[start - 1 : cursor]) <= max_width:
        start -= 1

    end = cursor
    while end < len(text) and measure(text[start : end + 1]) <= max_width:
        end += 1

    visible = text[start:end]
    cursor_offset = cursor - start
    return (visible, cursor_offset)
