from __future__ import annotations

import time

from .input import Action
from .models import AppMode, ConfirmOverlayState, MenuOverlayState, TextInputOverlayState


class ControllerRepeatMixin:
    def repeatable_virtual_key(self, key: str) -> bool:
        return key not in {"SHIFT", "LANG", "SYM", "ABC", "ENTER"}

    def text_entry_repeat_allowed(self, action: Action) -> bool:
        if action == Action.CONFIRM:
            return self.repeatable_virtual_key(self.editor.selected_key())
        return action in {
            Action.DELETE,
            Action.SPACE,
            Action.CURSOR_LEFT,
            Action.CURSOR_RIGHT,
            Action.CURSOR_LINE_UP,
            Action.CURSOR_LINE_DOWN,
            Action.NAV_UP,
            Action.NAV_DOWN,
            Action.NAV_LEFT,
            Action.NAV_RIGHT,
        }

    def start_key_repeat(self, sym: int) -> None:
        if self.repeat_action_allowed(sym):
            self.state.held_keys[sym] = time.monotonic() + self.state.repeat_delay

    def stop_key_repeat(self, sym: int) -> None:
        self.state.held_keys.pop(sym, None)

    def repeat_action_allowed(self, sym: int) -> bool:
        action = self.resolve(sym)
        if not action:
            return False

        if isinstance(self.state.overlay, TextInputOverlayState):
            return self.text_entry_repeat_allowed(action)
        if isinstance(self.state.overlay, MenuOverlayState):
            return action in {Action.NAV_UP, Action.NAV_DOWN}
        if isinstance(self.state.overlay, ConfirmOverlayState):
            return action in {Action.NAV_LEFT, Action.NAV_RIGHT}
        if self.state.mode == AppMode.EDIT:
            return self.text_entry_repeat_allowed(action)
        if self.state.mode in {AppMode.LIST, AppMode.PREVIEW}:
            return action in {Action.NAV_UP, Action.NAV_DOWN, Action.CURSOR_LINE_UP, Action.CURSOR_LINE_DOWN}
        if self.state.mode in {AppMode.SETTINGS, AppMode.LAYOUTS}:
            return action in {Action.NAV_UP, Action.NAV_DOWN}
        return False

    def perform_text_entry_repeat_action(self, action: Action) -> bool:
        if action == Action.CONFIRM:
            key = self.editor.selected_key()
            if self.repeatable_virtual_key(key):
                self.editor.activate_virtual_key(key)
                return True
            return False

        handlers = {
            Action.DELETE: self.editor.backspace,
            Action.SPACE: lambda: self.editor.insert_text(" "),
            Action.CURSOR_LEFT: lambda: self.editor.move_cursor_horizontal(-1),
            Action.CURSOR_RIGHT: lambda: self.editor.move_cursor_horizontal(1),
            Action.CURSOR_LINE_UP: lambda: self.editor.move_cursor_vertical(-1),
            Action.CURSOR_LINE_DOWN: lambda: self.editor.move_cursor_vertical(1),
            Action.NAV_UP: lambda: self.editor.keyboard_move(0, -1),
            Action.NAV_DOWN: lambda: self.editor.keyboard_move(0, 1),
            Action.NAV_LEFT: lambda: self.editor.keyboard_move(-1, 0),
            Action.NAV_RIGHT: lambda: self.editor.keyboard_move(1, 0),
        }
        handler = handlers.get(action)
        if handler is None:
            return False
        handler()
        return True

    def perform_repeat_action(self, sym: int) -> bool:
        action = self.resolve(sym)
        if not action:
            return False

        if isinstance(self.state.overlay, TextInputOverlayState):
            return self.perform_text_entry_repeat_action(action)

        if isinstance(self.state.overlay, MenuOverlayState):
            if action == Action.NAV_UP:
                self.move_menu_selection(-1)
                return True
            if action == Action.NAV_DOWN:
                self.move_menu_selection(1)
                return True
            return False

        if isinstance(self.state.overlay, ConfirmOverlayState):
            if action in {Action.NAV_LEFT, Action.NAV_RIGHT}:
                self.toggle_confirm_selection()
                return True
            return False

        if self.state.mode == AppMode.EDIT:
            return self.perform_text_entry_repeat_action(action)

        if self.state.mode == AppMode.LIST:
            if action == Action.NAV_UP:
                self.move_note_selection(-1)
                return True
            if action == Action.NAV_DOWN:
                self.move_note_selection(1)
                return True
            if action == Action.CURSOR_LINE_UP:
                self.move_note_selection(-5)
                return True
            if action == Action.CURSOR_LINE_DOWN:
                self.move_note_selection(5)
                return True
            return False

        if self.state.mode == AppMode.PREVIEW:
            if action in {Action.NAV_UP, Action.CURSOR_LINE_UP}:
                self.move_preview_selection(-1)
                return True
            if action in {Action.NAV_DOWN, Action.CURSOR_LINE_DOWN}:
                self.move_preview_selection(1)
                return True
            return False

        if self.state.mode == AppMode.SETTINGS:
            if action == Action.NAV_UP:
                self.move_settings_selection(-1, 6)
                return True
            if action == Action.NAV_DOWN:
                self.move_settings_selection(1, 6)
                return True
            return False

        if self.state.mode == AppMode.LAYOUTS:
            if action == Action.NAV_UP:
                self.move_layout_selection(-1)
                return True
            if action == Action.NAV_DOWN:
                self.move_layout_selection(1)
                return True
            return False

        return False

    def process_key_repeats(self) -> None:
        now = time.monotonic()
        for sym, next_at in list(self.state.held_keys.items()):
            if now < next_at:
                continue
            if self.perform_repeat_action(sym):
                self.state.held_keys[sym] = now + self.state.repeat_interval
            else:
                self.stop_key_repeat(sym)
