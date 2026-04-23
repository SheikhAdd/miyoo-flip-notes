from __future__ import annotations

from .constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_2,
    COLOR_BG_2,
    COLOR_DANGER,
    COLOR_KEY,
    COLOR_KEY_SEL,
    COLOR_KEY_TEXT,
    COLOR_MUTED,
    COLOR_OVERLAY,
    COLOR_PANEL,
    COLOR_PANEL_3,
    COLOR_TEXT,
    TEXT_DIALOG_FIELD_INNER_W,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
)
from .layouts import get_layout
from .models import ConfirmOverlayState, MenuOverlayState, TextInputOverlayState
from .render_layout import confirm_overlay_layout, keyboard_layout, menu_overlay_layout, text_dialog_layout
from .viewports import fit_cursor_window


class RenderOverlaysMixin:
    def render_overlay(self, state) -> None:
        self.fill_rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_OVERLAY)
        if isinstance(state.overlay, MenuOverlayState):
            self.render_menu_overlay(state.overlay)
        elif isinstance(state.overlay, ConfirmOverlayState):
            self.render_confirm_overlay(state.overlay)
        elif isinstance(state.overlay, TextInputOverlayState):
            self.render_text_input_overlay(state.overlay, state)

    def render_menu_overlay(self, overlay: MenuOverlayState) -> None:
        layout = menu_overlay_layout(len(overlay.options))
        self.draw_panel(layout.box.x, layout.box.y, layout.box.w, layout.box.h, COLOR_PANEL, COLOR_ACCENT)
        self.draw_text(overlay.title, layout.box.x + 14, layout.box.y + 14, self.font_title, COLOR_TEXT, layout.box.w - 28)
        for index, option in enumerate(overlay.options):
            selected = index == overlay.selected
            row_rect = layout.option_rects[index]
            self.fill_rect(row_rect.x, row_rect.y, row_rect.w, row_rect.h, COLOR_KEY_SEL if selected else COLOR_KEY)
            self.draw_text(option.label, row_rect.x + 10, row_rect.y + 8, self.font_ui, COLOR_KEY_TEXT, row_rect.w - 20)

    def render_confirm_overlay(self, overlay: ConfirmOverlayState) -> None:
        layout = confirm_overlay_layout(len(overlay.options))
        self.draw_panel(layout.box.x, layout.box.y, layout.box.w, layout.box.h, COLOR_PANEL, COLOR_DANGER)
        self.draw_text(overlay.title, layout.box.x + 14, layout.box.y + 14, self.font_title, COLOR_TEXT, layout.box.w - 28)
        lines = self.wrap_text(overlay.message, self.font_ui, layout.text_width)
        text_y = layout.text_y
        for line in lines[:3]:
            self.draw_text(line, layout.text_x, text_y, self.font_ui, COLOR_MUTED, layout.text_width)
            text_y += 20
        for index, option in enumerate(overlay.options):
            selected = index == overlay.selected
            button_rect = layout.button_rects[index]
            self.fill_rect(button_rect.x, button_rect.y, button_rect.w, button_rect.h, COLOR_DANGER if selected else COLOR_KEY)
            self.draw_text(option.label, button_rect.x + 12, button_rect.y + 8, self.font_ui, COLOR_KEY_TEXT, button_rect.w - 24)

    def render_text_input_overlay(self, overlay: TextInputOverlayState, state) -> None:
        layout = text_dialog_layout()
        self.draw_panel(layout.box.x, layout.box.y, layout.box.w, layout.box.h, COLOR_PANEL, COLOR_ACCENT)
        self.draw_text(overlay.title, layout.title_x, layout.title_y, self.font_title, COLOR_TEXT, layout.box.w - 28)
        if overlay.message:
            self.draw_text(overlay.message, layout.message_x, layout.message_y, self.font_small, COLOR_MUTED, layout.box.w - 28)

        field = layout.field_rect
        self.draw_panel(field.x, field.y, field.w, field.h, COLOR_BG_2, COLOR_PANEL_3)
        visible_text, cursor_offset = fit_cursor_window(
            overlay.text,
            overlay.cursor,
            TEXT_DIALOG_FIELD_INNER_W,
            lambda value: self.measure(value, self.font_ui)[0],
        )
        self.draw_text(visible_text or " ", layout.field_text_x, layout.field_text_y, self.font_ui, COLOR_TEXT, TEXT_DIALOG_FIELD_INNER_W)

        prefix = visible_text[:cursor_offset]
        cursor_x = layout.field_text_x + self.measure(prefix, self.font_ui)[0]
        self.fill_rect(cursor_x, field.y + 10, 2, 20, COLOR_ACCENT_2)

        if overlay.error:
            self.draw_text(overlay.error, layout.error_x, layout.error_y, self.font_small, COLOR_DANGER, layout.box.w - 32)

        self.render_keyboard(state, layout.keyboard_y)

    def display_key_label(self, key: str, shift: bool) -> str:
        labels = {
            "SHIFT": "Shift",
            "BACK": "Del",
            "SPACE": "Space",
            "LANG": "Lang",
            "SYM": "123",
            "ABC": "ABC",
            "LEFT": "<",
            "RIGHT": ">",
            "ENTER": "Enter",
        }
        if key in labels:
            return labels[key]
        if len(key) == 1 and shift and key.isalpha():
            return key.upper()
        return key

    def render_keyboard(self, state, y0: int) -> None:
        rows = get_layout(state.layout_id).rows
        for cell in keyboard_layout(rows, y0):
            selected = cell.row_index == state.key_row and cell.col_index == state.key_col
            fill = COLOR_KEY_SEL if selected else COLOR_KEY
            border = COLOR_ACCENT if selected else COLOR_PANEL_3
            self.draw_panel(cell.rect.x, cell.rect.y, cell.rect.w, cell.rect.h, fill, border)
            label = self.display_key_label(cell.key, state.shift)
            text_w, text_h = self.measure(label, self.font_key)
            self.draw_text(
                label,
                cell.rect.x + max(6, (cell.rect.w - text_w) // 2),
                cell.rect.y + max(3, (cell.rect.h - text_h) // 2),
                self.font_key,
                COLOR_KEY_TEXT,
            )
