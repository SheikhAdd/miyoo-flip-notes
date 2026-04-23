from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    EDITOR_KEYBOARD_Y,
    EDITOR_TEXT_BOTTOM_GAP,
    EDITOR_TEXT_H,
    EDITOR_TEXT_PADDING,
    EDITOR_TEXT_W,
    EDITOR_TEXT_X,
    EDITOR_TEXT_Y,
    FOOTER_HEIGHT,
    LAYOUTS_VISIBLE_ROWS,
    LIST_VISIBLE_ROWS,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    TEXT_DIALOG_FIELD_W,
    TEXT_DIALOG_FIELD_Y,
    TEXT_DIALOG_H,
    TEXT_DIALOG_KEYBOARD_Y,
    TEXT_DIALOG_W,
    TEXT_DIALOG_X,
    TEXT_DIALOG_Y,
)
from .keyboard_geometry import key_weight


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h


@dataclass(frozen=True)
class HeaderLayout:
    title_x: int
    title_y: int
    subtitle_x: int
    subtitle_y: int
    subtitle_max_width: int
    right_x: int
    right_y: int


@dataclass(frozen=True)
class EditorLayout:
    text_rect: Rect
    scroll_x: int
    scroll_y: int
    keyboard_y: int
    max_cols: int
    visible_rows: int


@dataclass(frozen=True)
class MenuOverlayLayout:
    box: Rect
    option_rects: list[Rect]


@dataclass(frozen=True)
class ConfirmOverlayLayout:
    box: Rect
    text_x: int
    text_y: int
    text_width: int
    button_rects: list[Rect]


@dataclass(frozen=True)
class TextDialogLayout:
    box: Rect
    title_x: int
    title_y: int
    message_x: int
    message_y: int
    field_rect: Rect
    field_text_x: int
    field_text_y: int
    error_x: int
    error_y: int
    keyboard_y: int


@dataclass(frozen=True)
class KeyboardKeyLayout:
    row_index: int
    col_index: int
    key: str
    rect: Rect


def header_layout(right_width: int = 0) -> HeaderLayout:
    return HeaderLayout(
        title_x=12,
        title_y=7,
        subtitle_x=12,
        subtitle_y=29,
        subtitle_max_width=max(80, LOGICAL_WIDTH - right_width - 36),
        right_x=LOGICAL_WIDTH - right_width - 12,
        right_y=16,
    )


def list_row_rect(row_index: int) -> Rect:
    row_height = 36
    y = 54 + row_index * row_height
    return Rect(12, y, LOGICAL_WIDTH - 24, row_height - 4)


def list_selected_text_y() -> int:
    return LOGICAL_HEIGHT - FOOTER_HEIGHT - 18


def editor_layout(char_width: int, line_height: int) -> EditorLayout:
    text_rect = Rect(EDITOR_TEXT_X, EDITOR_TEXT_Y, EDITOR_TEXT_W, EDITOR_TEXT_H)
    max_cols = max(20, (text_rect.w - 14) // max(1, char_width))
    visible_rows = max(3, (text_rect.h - 12) // max(1, line_height))
    return EditorLayout(
        text_rect=text_rect,
        scroll_x=LOGICAL_WIDTH - 130,
        scroll_y=text_rect.bottom + EDITOR_TEXT_BOTTOM_GAP,
        keyboard_y=EDITOR_KEYBOARD_Y,
        max_cols=max_cols,
        visible_rows=visible_rows,
    )


def preview_panel_rect() -> Rect:
    panel_y = 52
    return Rect(14, panel_y, LOGICAL_WIDTH - 28, LOGICAL_HEIGHT - panel_y - FOOTER_HEIGHT - 8)


def settings_row_rect(row_index: int) -> Rect:
    row_height = 52
    y = 70 + row_index * row_height
    return Rect(18, y, LOGICAL_WIDTH - 36, row_height - 6)


def layouts_row_rect(row_index: int) -> Rect:
    row_height = 44
    y = 68 + row_index * row_height
    return Rect(18, y, LOGICAL_WIDTH - 36, row_height - 4)


def menu_overlay_layout(option_count: int) -> MenuOverlayLayout:
    box = Rect(88, 74, LOGICAL_WIDTH - 176, 62 + option_count * 38)
    option_rects = [
        Rect(box.x + 10, box.y + 50 + index * 36, box.w - 20, 30)
        for index in range(option_count)
    ]
    return MenuOverlayLayout(box=box, option_rects=option_rects)


def confirm_overlay_layout(button_count: int = 2) -> ConfirmOverlayLayout:
    box = Rect(74, 92, LOGICAL_WIDTH - 148, 162)
    button_width = (box.w - 52) // max(1, button_count)
    button_gap = 8
    button_y = box.bottom - 48
    button_rects = [
        Rect(box.x + 16 + index * (button_width + button_gap), button_y, button_width, 30)
        for index in range(button_count)
    ]
    return ConfirmOverlayLayout(
        box=box,
        text_x=box.x + 14,
        text_y=box.y + 52,
        text_width=box.w - 28,
        button_rects=button_rects,
    )


def text_dialog_layout() -> TextDialogLayout:
    box = Rect(TEXT_DIALOG_X, TEXT_DIALOG_Y, TEXT_DIALOG_W, TEXT_DIALOG_H)
    field = Rect(box.x + 14, TEXT_DIALOG_FIELD_Y, TEXT_DIALOG_FIELD_W, 42)
    return TextDialogLayout(
        box=box,
        title_x=box.x + 14,
        title_y=box.y + 12,
        message_x=box.x + 14,
        message_y=box.y + 40,
        field_rect=field,
        field_text_x=field.x + 10,
        field_text_y=field.y + 12,
        error_x=box.x + 16,
        error_y=box.bottom - 16,
        keyboard_y=TEXT_DIALOG_KEYBOARD_Y,
    )


def keyboard_layout(rows: list[list[str]], y0: int) -> list[KeyboardKeyLayout]:
    row_height = 34
    gap = 4
    x0 = 14
    available_width = LOGICAL_WIDTH - 28
    cells: list[KeyboardKeyLayout] = []
    for row_index, row in enumerate(rows):
        total_weight = sum(key_weight(key) for key in row)
        unit = (available_width - gap * (len(row) - 1)) // max(1, total_weight)
        x = x0
        for col_index, key in enumerate(row):
            width = max(24, unit * key_weight(key))
            cells.append(
                KeyboardKeyLayout(
                    row_index=row_index,
                    col_index=col_index,
                    key=key,
                    rect=Rect(x, y0 + row_index * (row_height + gap), width, row_height),
                )
            )
            x += width + gap
    return cells


def visible_note_rows() -> int:
    return LIST_VISIBLE_ROWS


def visible_layout_rows() -> int:
    return LAYOUTS_VISIBLE_ROWS


def editor_text_padding() -> int:
    return EDITOR_TEXT_PADDING
