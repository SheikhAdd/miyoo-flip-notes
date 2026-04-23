from __future__ import annotations

import time

from .constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_2,
    COLOR_BG,
    COLOR_BG_2,
    COLOR_MUTED,
    COLOR_PANEL,
    COLOR_PANEL_2,
    COLOR_PANEL_3,
    COLOR_TEXT,
    COLOR_WARN,
    FOOTER_HEIGHT,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
)
from .layouts import LAYOUT_ORDER, get_layout
from .models import (
    AppMode,
    PreviewStyle,
)
from .render_layout import (
    editor_layout,
    editor_text_padding,
    header_layout,
    layouts_row_rect,
    list_row_rect,
    list_selected_text_y,
    preview_panel_rect,
    settings_row_rect,
    visible_layout_rows,
    visible_note_rows,
)
from .render_overlays import RenderOverlaysMixin
from .texts import PREVIEW_BADGE, footer_text, settings_rows


class RenderViewsMixin(RenderOverlaysMixin):
    def render(self, state) -> None:
        self.fill_rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG)
        self.fill_rect(0, 0, LOGICAL_WIDTH, 42, COLOR_BG_2)
        self.fill_rect(0, LOGICAL_HEIGHT - FOOTER_HEIGHT, LOGICAL_WIDTH, FOOTER_HEIGHT, (10, 13, 16, 255))

        if state.mode == AppMode.LIST:
            self.render_list(state)
        elif state.mode == AppMode.EDIT:
            self.render_editor(state)
        elif state.mode == AppMode.PREVIEW:
            self.render_preview(state)
        elif state.mode == AppMode.SETTINGS:
            self.render_settings(state)
        elif state.mode == AppMode.LAYOUTS:
            self.render_layouts(state)

        if state.overlay:
            self.render_overlay(state)

        self.draw_text(footer_text(state), 10, LOGICAL_HEIGHT - 18, self.font_small, COLOR_MUTED, LOGICAL_WIDTH - 20)
        self.sdl2.SDL_RenderPresent(self.renderer)

    def render_header(self, title: str, subtitle: str = "", right: str = "") -> None:
        layout = header_layout(self.measure(right, self.font_small)[0] if right else 0)
        self.draw_text(title, layout.title_x, layout.title_y, self.font_title, COLOR_TEXT)
        if subtitle:
            self.draw_text(subtitle, layout.subtitle_x, layout.subtitle_y, self.font_small, COLOR_MUTED, layout.subtitle_max_width)
        if right:
            self.draw_text(right, layout.right_x, layout.right_y, self.font_small, COLOR_ACCENT)

    def render_list(self, state) -> None:
        count = f"{len(state.notes)} notes"
        self.render_header("Notes", "", count)

        visible = state.notes[state.list_scroll : state.list_scroll + visible_note_rows()]
        for row_index, record in enumerate(visible):
            note_index = state.list_scroll + row_index
            selected = note_index == state.selected_note
            fill = COLOR_PANEL_2 if selected else COLOR_PANEL
            row_rect = list_row_rect(row_index)
            self.draw_panel(row_rect.x, row_rect.y, row_rect.w, row_rect.h, fill, COLOR_ACCENT if selected else COLOR_PANEL_3)
            mtime = time.strftime("%d.%m.%Y %H:%M", time.localtime(record.modified_at))
            self.draw_text(record.title, row_rect.x + 12, row_rect.y + 7, self.font_ui, COLOR_TEXT, 360)
            self.draw_text(mtime, row_rect.right - 140, row_rect.y + 10, self.font_small, COLOR_MUTED, 120)

        if state.notes:
            selected = state.notes[min(state.selected_note, len(state.notes) - 1)]
            self.draw_text(
                "Selected: " + selected.title,
                12,
                list_selected_text_y(),
                self.font_small,
                COLOR_MUTED,
                LOGICAL_WIDTH - 24,
            )

    def render_editor(self, state) -> None:
        title = state.current_path.stem if state.current_path else "Untitled"
        marker = " *" if state.dirty else ""
        layout_short = get_layout(state.layout_id).short
        autosave_subtitle = (
            f"Autosave every {state.config.autosave_minutes} min" if state.config.autosave_enabled else "Autosave is disabled"
        )
        self.render_header(title + marker, autosave_subtitle, layout_short)

        layout = editor_layout(state.char_width, state.line_height)
        text_rect = layout.text_rect
        self.draw_panel(text_rect.x, text_rect.y, text_rect.w, text_rect.h, COLOR_PANEL, COLOR_PANEL_3)

        lines, cursor_line, cursor_col = self.visual_lines(state.text, state.cursor, layout.max_cols)

        for row, line in enumerate(lines[state.text_scroll : state.text_scroll + layout.visible_rows]):
            self.draw_text(
                line,
                text_rect.x + editor_text_padding(),
                text_rect.y + 6 + row * state.line_height,
                self.font_text,
                COLOR_TEXT,
                text_rect.w - 16,
            )

        cursor_visible_row = cursor_line - state.text_scroll
        if 0 <= cursor_visible_row < layout.visible_rows:
            cx = text_rect.x + editor_text_padding() + cursor_col * state.char_width
            cy = text_rect.y + editor_text_padding() + cursor_visible_row * state.line_height
            self.fill_rect(cx, cy, 2, state.line_height - 4, COLOR_ACCENT_2)

        self.draw_text(
            f"Scroll {state.text_scroll + 1}/{max(state.text_scroll + layout.visible_rows, len(lines))}",
            layout.scroll_x,
            layout.scroll_y,
            self.font_small,
            COLOR_MUTED,
        )
        self.render_keyboard(state, layout.keyboard_y)

    def render_preview(self, state) -> None:
        self.render_header("Preview", state.preview_title, PREVIEW_BADGE)
        panel = preview_panel_rect()
        self.draw_panel(panel.x, panel.y, panel.w, panel.h, COLOR_PANEL, COLOR_PANEL_3)

        y = panel.y + 8
        bottom = panel.bottom - 8
        index = max(0, min(state.preview_scroll, max(0, len(state.preview_lines) - 1)))
        while index < len(state.preview_lines):
            item = state.preview_lines[index]
            if y + item.height > bottom:
                break
            font = self.preview_font(item.style)
            color = self.preview_color(item.style)
            if item.style == PreviewStyle.CODE:
                self.fill_rect(panel.x + 8, y - 1, panel.w - 16, item.height, (20, 24, 29, 255))
            if item.style == PreviewStyle.QUOTE:
                self.fill_rect(panel.x + 8, y, 3, item.height - 2, COLOR_WARN)
            self.draw_text(
                item.text,
                panel.x + 12 + item.indent,
                y,
                font,
                color,
                panel.w - 28 - item.indent,
            )
            y += item.height
            index += 1

    def render_settings(self, state) -> None:
        self.render_header("Settings")
        rows = settings_rows(state.config)
        for index, (label, value) in enumerate(rows):
            selected = index == state.settings_index
            fill = COLOR_PANEL_2 if selected else COLOR_PANEL
            row_rect = settings_row_rect(index)
            self.draw_panel(row_rect.x, row_rect.y, row_rect.w, row_rect.h, fill, COLOR_ACCENT if selected else COLOR_PANEL_3)
            self.draw_text(label, row_rect.x + 12, row_rect.y + 7, self.font_ui, COLOR_TEXT, 240)
            self.draw_text(value, row_rect.x + 12, row_rect.y + 26, self.font_small, COLOR_MUTED, LOGICAL_WIDTH - 96)

    def render_layouts(self, state) -> None:
        self.render_header("Layouts")
        active = set(state.config.active_layouts)
        order = list(LAYOUT_ORDER)
        visible = order[state.layouts_scroll : state.layouts_scroll + visible_layout_rows()]
        for index, layout_id in enumerate(visible):
            real_index = state.layouts_scroll + index
            layout = get_layout(layout_id)
            selected = real_index == state.layouts_index
            fill = COLOR_PANEL_2 if selected else COLOR_PANEL
            border = COLOR_ACCENT if selected else COLOR_PANEL_3
            row_rect = layouts_row_rect(index)
            self.draw_panel(row_rect.x, row_rect.y, row_rect.w, row_rect.h, fill, border)
            tag = "[x]" if layout_id in active else "[ ]"
            self.draw_text(f"{tag} {layout.short}", row_rect.x + 12, row_rect.y + 8, self.font_ui, COLOR_ACCENT if layout_id in active else COLOR_MUTED)
            self.draw_text(layout.title, row_rect.x + 72, row_rect.y + 8, self.font_ui, COLOR_TEXT, 280)
            self.draw_text(layout.family.value, row_rect.right - 72, row_rect.y + 10, self.font_small, COLOR_MUTED, 60)
