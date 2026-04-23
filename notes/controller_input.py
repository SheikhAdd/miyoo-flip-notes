from __future__ import annotations

from .controller_repeat import ControllerRepeatMixin
from .input import Action, resolve_action
from .models import AppMode, ConfirmOverlayState, MenuOverlayState, TextInputOverlayState


class ControllerInputMixin(ControllerRepeatMixin):
    def handle_text_input(self, value: str) -> None:
        if value and all(ord(ch) >= 32 for ch in value):
            if self.editor.text_dialog_active() or self.state.mode == AppMode.EDIT:
                self.editor.insert_text(value)

    def handle_key(self, sym: int) -> bool:
        if self.state.overlay:
            return self.handle_overlay_key(sym)
        if self.state.mode == AppMode.LIST:
            return self.handle_list_key(sym)
        if self.state.mode == AppMode.EDIT:
            return self.handle_editor_key(sym)
        if self.state.mode == AppMode.PREVIEW:
            return self.handle_preview_key(sym)
        if self.state.mode == AppMode.SETTINGS:
            return self.handle_settings_key(sym)
        if self.state.mode == AppMode.LAYOUTS:
            return self.handle_layouts_key(sym)
        return True

    def resolve(self, sym: int) -> Action | None:
        return resolve_action(self.sdl2, self.state.config, sym)

    def handle_overlay_key(self, sym: int) -> bool:
        action = self.resolve(sym)

        if isinstance(self.state.overlay, MenuOverlayState):
            return self.handle_menu_overlay_action(action)

        if isinstance(self.state.overlay, ConfirmOverlayState):
            return self.handle_confirm_overlay_action(action)

        if isinstance(self.state.overlay, TextInputOverlayState):
            if action == Action.CANCEL:
                self.close_overlay()
                return True
            return self.handle_text_entry_action(action, dialog_mode=True)

        return True

    def handle_menu_overlay_action(self, action: Action | None) -> bool:
        if action == Action.CANCEL:
            self.close_overlay()
        elif action == Action.NAV_UP:
            self.move_menu_selection(-1)
        elif action == Action.NAV_DOWN:
            self.move_menu_selection(1)
        elif action in {Action.CONFIRM, Action.ENTER}:
            self.handle_menu_confirm()
        return True

    def handle_confirm_overlay_action(self, action: Action | None) -> bool:
        if action == Action.CANCEL:
            self.close_overlay()
        elif action in {Action.NAV_LEFT, Action.NAV_RIGHT}:
            self.toggle_confirm_selection()
        elif action in {Action.CONFIRM, Action.ENTER}:
            self.handle_confirm_overlay()
        return True

    def handle_list_key(self, sym: int) -> bool:
        action = self.resolve(sym)
        if action == Action.CANCEL:
            return False
        if action == Action.NAV_UP:
            self.move_note_selection(-1)
        elif action == Action.NAV_DOWN:
            self.move_note_selection(1)
        elif action == Action.CURSOR_LINE_UP:
            self.move_note_selection(-5)
        elif action == Action.CURSOR_LINE_DOWN:
            self.move_note_selection(5)
        elif action in {Action.CONFIRM, Action.ENTER}:
            selected = self.notes.current_selected_path()
            if selected:
                self.notes.open_note(selected)
        elif action == Action.SPACE:
            self.open_new_note_dialog()
        elif action == Action.TOGGLE_SHIFT:
            self.open_note_menu()
        elif action == Action.MENU:
            self.state.settings_index = 0
            self.open_settings()
        return True

    def handle_editor_key(self, sym: int) -> bool:
        action = self.resolve(sym)
        if action == Action.CANCEL:
            if self.notes.ensure_note_saved():
                self.notes.refresh_notes()
                self.state.mode = AppMode.LIST
            return True
        if action == Action.MENU:
            self.open_note_menu()
            return True
        return self.handle_text_entry_action(action, dialog_mode=False)

    def handle_preview_key(self, sym: int) -> bool:
        action = self.resolve(sym)
        if action == Action.CANCEL:
            self.state.mode = self.state.preview_return_mode
            return True
        if action == Action.MENU:
            self.open_note_menu()
        elif action in {Action.NAV_UP, Action.CURSOR_LINE_UP}:
            self.move_preview_selection(-1)
        elif action in {Action.NAV_DOWN, Action.CURSOR_LINE_DOWN}:
            self.move_preview_selection(1)
        return True

    def handle_settings_key(self, sym: int) -> bool:
        action = self.resolve(sym)
        rows = 6
        if action == Action.CANCEL:
            self.state.mode = AppMode.LIST
            self.notes.refresh_notes()
            return True
        if action == Action.NAV_UP:
            self.move_settings_selection(-1, rows)
        elif action == Action.NAV_DOWN:
            self.move_settings_selection(1, rows)
        elif action in {Action.CONFIRM, Action.ENTER}:
            if self.state.settings_index == 0:
                self.settings.toggle_button_scheme()
            elif self.state.settings_index == 1:
                self.settings.toggle_autosave()
            elif self.state.settings_index == 2:
                self.settings.cycle_autosave_minutes()
            elif self.state.settings_index == 3:
                self.settings.cycle_text_scale()
            elif self.state.settings_index == 4:
                self.state.mode = AppMode.LAYOUTS
                self.state.layouts_index = 0
                self.state.layouts_scroll = 0
            elif self.state.settings_index == 5:
                self.state.mode = AppMode.LIST
                self.notes.refresh_notes()
        return True

    def handle_layouts_key(self, sym: int) -> bool:
        action = self.resolve(sym)
        if action == Action.CANCEL:
            self.state.mode = AppMode.SETTINGS
            self.state.settings_index = 4
            return True
        if action == Action.NAV_UP:
            self.move_layout_selection(-1)
        elif action == Action.NAV_DOWN:
            self.move_layout_selection(1)
        elif action in {Action.CONFIRM, Action.ENTER}:
            order = self.layouts.layout_order()
            if 0 <= self.state.layouts_index < len(order):
                self.settings.toggle_layout_enabled(order[self.state.layouts_index])
        return True

    def handle_text_entry_action(self, action: Action | None, dialog_mode: bool) -> bool:
        if action is None:
            return True
        if action == Action.CONFIRM:
            self.editor.press_virtual_key()
            return True
        if action == Action.ENTER:
            if dialog_mode:
                self.confirm_text_dialog()
            else:
                self.editor.insert_text("\n")
            return True

        handlers = {
            Action.DELETE: self.editor.backspace,
            Action.SPACE: lambda: self.editor.insert_text(" "),
            Action.TOGGLE_SHIFT: self.editor.toggle_shift_state,
            Action.TOGGLE_SYMBOLS: self.layouts.toggle_symbols_layout,
            Action.NAV_UP: lambda: self.editor.keyboard_move(0, -1),
            Action.NAV_DOWN: lambda: self.editor.keyboard_move(0, 1),
            Action.NAV_LEFT: lambda: self.editor.keyboard_move(-1, 0),
            Action.NAV_RIGHT: lambda: self.editor.keyboard_move(1, 0),
            Action.PREV_LAYOUT: lambda: self.layouts.cycle_layout(-1),
            Action.NEXT_LAYOUT: lambda: self.layouts.cycle_layout(1),
            Action.CURSOR_LEFT: lambda: self.editor.move_cursor_horizontal(-1),
            Action.CURSOR_RIGHT: lambda: self.editor.move_cursor_horizontal(1),
            Action.CURSOR_LINE_UP: lambda: self.editor.move_cursor_vertical(-1),
            Action.CURSOR_LINE_DOWN: lambda: self.editor.move_cursor_vertical(1),
        }
        handler = handlers.get(action)
        if handler is not None:
            handler()
        return True

    def move_menu_selection(self, delta: int) -> None:
        if not isinstance(self.state.overlay, MenuOverlayState):
            return
        last_index = len(self.state.overlay.options) - 1
        self.state.overlay.selected = max(0, min(last_index, self.state.overlay.selected + delta))

    def toggle_confirm_selection(self) -> None:
        if isinstance(self.state.overlay, ConfirmOverlayState):
            self.state.overlay.selected = 1 - self.state.overlay.selected

    def move_note_selection(self, delta: int) -> None:
        self.state.selected_note = min(max(0, len(self.state.notes) - 1), max(0, self.state.selected_note + delta))
        self.notes.ensure_note_visible()

    def move_preview_selection(self, delta: int) -> None:
        self.state.preview_scroll = min(max(0, len(self.state.preview_lines) - 1), max(0, self.state.preview_scroll + delta))

    def move_settings_selection(self, delta: int, rows: int) -> None:
        self.state.settings_index = max(0, min(rows - 1, self.state.settings_index + delta))

    def move_layout_selection(self, delta: int) -> None:
        count = len(self.layouts.layout_order())
        self.state.layouts_index = max(0, min(count - 1, self.state.layouts_index + delta))
        self.settings.ensure_layout_visible()
