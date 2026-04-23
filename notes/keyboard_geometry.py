from __future__ import annotations

from .utils import clamp


def key_weight(key: str) -> int:
    weights = {
        "SHIFT": 2,
        "BACK": 2,
        "SPACE": 4,
        "LANG": 2,
        "SYM": 2,
        "ABC": 2,
        "ENTER": 2,
        "LEFT": 1,
        "RIGHT": 1,
    }
    return weights.get(key, 1)


def row_centers(row: list[str], gap: int = 1) -> list[float]:
    centers: list[float] = []
    x = 0.0
    for index, key in enumerate(row):
        width = float(key_weight(key))
        centers.append(x + width / 2.0)
        x += width
        if index < len(row) - 1:
            x += gap
    return centers


def closest_column(row: list[str], x_center: float) -> int:
    centers = row_centers(row)
    return min(range(len(centers)), key=lambda index: abs(centers[index] - x_center))


def remap_selection(
    old_rows: list[list[str]],
    new_rows: list[list[str]],
    old_row: int,
    old_col: int,
) -> tuple[int, int]:
    row_index = clamp(old_row, 0, len(new_rows) - 1)
    if not old_rows:
        return (row_index, 0)
    source_row = old_rows[clamp(old_row, 0, len(old_rows) - 1)]
    source_col = clamp(old_col, 0, len(source_row) - 1)
    x_center = row_centers(source_row)[source_col]
    return (row_index, closest_column(new_rows[row_index], x_center))


def move_selection(rows: list[list[str]], row: int, col: int, dx: int, dy: int) -> tuple[int, int]:
    next_row = (row + dy) % len(rows)
    if dy == 0:
        return (next_row, clamp(col + dx, 0, len(rows[next_row]) - 1))

    current_row = rows[clamp(row, 0, len(rows) - 1)]
    current_col = clamp(col, 0, len(current_row) - 1)
    x_center = row_centers(current_row)[current_col]
    target_col = closest_column(rows[next_row], x_center)
    return (next_row, target_col)

