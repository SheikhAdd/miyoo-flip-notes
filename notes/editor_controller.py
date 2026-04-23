from __future__ import annotations

from typing import Callable, Protocol

from .constants import EDITOR_TEXT_H, EDITOR_TEXT_W, LOGICAL_WIDTH
from .editor_ops import delete_backward, insert_text as insert_text_op, move_horizontal, move_line_end, move_line_start, move_vertical, visual_lines
from .keyboard_geometry import move_selection
from .layout_manager import LayoutManager
from .layouts import get_layout
from .models import AppMode, AppState, PreviewLine, TextInputOverlayState
from .note_manager import NoteManager
from .storage import NoteRepository, StorageError
from .utils import clamp
from .viewports import clamp_scroll


class SupportsEditorUi(Protocol):
    def build_preview(self, markdown: str) -> list[PreviewLine]: ...


class EditorController:
    def __init__(
        self,
        state: AppState,
        ui: SupportsEditorUi,
        repository: NoteRepository,
        notes: NoteManager,
        layouts: LayoutManager,
        flash_status: Callable[[str], None],
        confirm_text_dialog: Callable[[], None],
    ) -> None:
        self.state = state
        self.ui = ui
        self.repository = repository
        self.notes = notes
        self.layouts = layouts
        self.flash_status = flash_status
        self.confirm_text_dialog = confirm_text_dialog

    def text_dialog_active(self) -> bool:
        return isinstance(self.state.overlay, TextInputOverlayState)

    def active_text_value(self) -> str:
        if isinstance(self.state.overlay, TextInputOverlayState):
            return self.state.overlay.text
        return self.state.text

    def set_active_text_value(self, value: str) -> None:
        if isinstance(self.state.overlay, TextInputOverlayState):
            self.state.overlay.text = value
            return
        self.state.text = value
        self.state.dirty = True
        self.state.follow_cursor = True

    def active_cursor(self) -> int:
        if isinstance(self.state.overlay, TextInputOverlayState):
            return self.state.overlay.cursor
        return self.state.cursor

    def set_active_cursor(self, value: int) -> None:
        clamped = clamp(value, 0, len(self.active_text_value()))
        if isinstance(self.state.overlay, TextInputOverlayState):
            self.state.overlay.cursor = clamped
            return
        self.state.cursor = clamped
        self.state.follow_cursor = True

    def insert_text(self, value: str) -> None:
        if not value:
            return
        updated, cursor = insert_text_op(self.active_text_value(), self.active_cursor(), value)
        self.set_active_text_value(updated)
        self.set_active_cursor(cursor)
        if isinstance(self.state.overlay, TextInputOverlayState):
            self.state.overlay.error = ""

    def backspace(self) -> None:
        updated, cursor = delete_backward(self.active_text_value(), self.active_cursor())
        self.set_active_text_value(updated)
        self.set_active_cursor(cursor)
        if isinstance(self.state.overlay, TextInputOverlayState):
            self.state.overlay.error = ""

    def move_cursor_horizontal(self, delta: int) -> None:
        self.set_active_cursor(move_horizontal(self.active_text_value(), self.active_cursor(), delta))

    def move_cursor_vertical(self, delta: int) -> None:
        if not self.state.current_path and not self.text_dialog_active():
            return
        text = self.active_text_value()
        cursor = self.active_cursor()
        max_cols = max(20, ((LOGICAL_WIDTH - 32) - 14) // max(1, self.state.char_width))
        self.set_active_cursor(move_vertical(text, cursor, max_cols, delta))

    def move_line_start(self) -> None:
        self.set_active_cursor(move_line_start(self.active_text_value(), self.active_cursor()))

    def move_line_end(self) -> None:
        self.set_active_cursor(move_line_end(self.active_text_value(), self.active_cursor()))

    def prepare_frame(self) -> None:
        if self.state.mode != AppMode.EDIT:
            return
        max_cols = max(20, (EDITOR_TEXT_W - 14) // max(1, self.state.char_width))
        lines, cursor_line, _ = visual_lines(self.state.text, self.state.cursor, max_cols)
        visible_rows = max(3, (EDITOR_TEXT_H - 12) // self.state.line_height)
        self.state.text_scroll = clamp_scroll(
            current_scroll=self.state.text_scroll,
            cursor_line=cursor_line,
            total_lines=len(lines),
            visible_rows=visible_rows,
            follow_cursor=self.state.follow_cursor,
        )

    def open_preview(self) -> None:
        self.state.held_keys.clear()
        title = ""
        markdown = ""
        if self.state.mode == AppMode.EDIT and self.state.current_path:
            title = self.state.current_path.stem
            markdown = self.state.text
            self.state.preview_return_mode = AppMode.EDIT
        else:
            selected = self.notes.current_selected_path()
            if not selected:
                return
            title = selected.stem
            try:
                markdown = self.repository.read_note(selected)
            except StorageError as exc:
                self.flash_status(str(exc))
                return
            self.state.preview_return_mode = AppMode.LIST
        self.state.preview_title = title
        self.state.preview_lines = self.ui.build_preview(markdown)
        self.state.preview_scroll = 0
        self.state.mode = AppMode.PREVIEW
        self.state.overlay = None

    def keyboard_move(self, dx: int, dy: int) -> None:
        rows = get_layout(self.state.layout_id).rows
        row, col = move_selection(rows, self.state.key_row, self.state.key_col, dx, dy)
        self.state.key_row = row
        self.state.key_col = col

    def selected_key(self) -> str:
        rows = get_layout(self.state.layout_id).rows
        self.state.key_row = clamp(self.state.key_row, 0, len(rows) - 1)
        self.state.key_col = clamp(self.state.key_col, 0, len(rows[self.state.key_row]) - 1)
        return rows[self.state.key_row][self.state.key_col]

    def transform_key(self, key: str) -> str:
        if len(key) == 1 and self.state.shift and key.isalpha():
            return key.upper()
        return key

    def press_virtual_key(self) -> None:
        self.activate_virtual_key(self.selected_key())

    def activate_virtual_key(self, key: str) -> None:
        if key == "SHIFT":
            self.toggle_shift_state()
        elif key == "BACK":
            self.backspace()
        elif key == "SPACE":
            self.insert_text(" ")
        elif key == "LEFT":
            self.move_cursor_horizontal(-1)
        elif key == "RIGHT":
            self.move_cursor_horizontal(1)
        elif key == "ENTER":
            if self.text_dialog_active():
                self.confirm_text_dialog()
            else:
                self.insert_text("\n")
        elif key == "LANG":
            self.layouts.cycle_alpha_layout()
        elif key == "SYM":
            self.layouts.switch_to_symbols()
        elif key == "ABC":
            self.layouts.switch_to_alpha()
        else:
            self.insert_text(self.transform_key(key))

    def toggle_shift_state(self) -> None:
        self.state.shift = not self.state.shift
