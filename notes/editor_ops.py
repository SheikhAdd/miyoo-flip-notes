from __future__ import annotations

from .utils import clamp


def insert_text(text: str, cursor: int, value: str) -> tuple[str, int]:
    updated = text[:cursor] + value + text[cursor:]
    return (updated, cursor + len(value))


def delete_backward(text: str, cursor: int) -> tuple[str, int]:
    if cursor <= 0:
        return (text, cursor)
    updated = text[: cursor - 1] + text[cursor:]
    return (updated, cursor - 1)


def move_horizontal(text: str, cursor: int, delta: int) -> int:
    return clamp(cursor + delta, 0, len(text))


def move_line_start(text: str, cursor: int) -> int:
    left = text.rfind("\n", 0, cursor)
    return 0 if left < 0 else left + 1


def move_line_end(text: str, cursor: int) -> int:
    right = text.find("\n", cursor)
    return len(text) if right < 0 else right


def visual_segments(text: str, cursor: int, max_cols: int) -> tuple[list[tuple[str, int, int]], int, int]:
    max_cols = max(8, max_cols)
    segments: list[tuple[str, int, int]] = []
    cursor_line = 0
    cursor_col = 0
    pos = 0
    logical_lines = text.split("\n")
    for line_index, logical in enumerate(logical_lines):
        chunks = [logical[index : index + max_cols] for index in range(0, len(logical), max_cols)] or [""]
        for chunk in chunks:
            start = pos
            end = pos + len(chunk)
            if start <= cursor <= end:
                cursor_line = len(segments)
                cursor_col = cursor - start
            segments.append((chunk, start, end))
            pos = end
        if line_index < len(logical_lines) - 1:
            if cursor == pos and segments:
                cursor_line = len(segments) - 1
                cursor_col = len(segments[-1][0])
            pos += 1
    if cursor >= len(text) and segments:
        cursor_line = max(0, len(segments) - 1)
        cursor_col = len(segments[cursor_line][0])
    if not segments:
        segments.append(("", 0, 0))
    return (segments, cursor_line, cursor_col)


def move_vertical(text: str, cursor: int, max_cols: int, delta: int) -> int:
    segments, cursor_line, cursor_col = visual_segments(text, cursor, max_cols)
    target_line = clamp(cursor_line + delta, 0, len(segments) - 1)
    target_text, target_start, _ = segments[target_line]
    return target_start + min(cursor_col, len(target_text))


def visual_lines(text: str, cursor: int, max_cols: int) -> tuple[list[str], int, int]:
    segments, cursor_line, cursor_col = visual_segments(text, cursor, max_cols)
    return ([segment[0] for segment in segments], cursor_line, cursor_col)

