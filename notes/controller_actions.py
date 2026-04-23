from __future__ import annotations

from pathlib import Path

from .models import (
    AppMode,
    ConfirmOverlayState,
    ConfirmPurpose,
    MenuAction,
    MenuOverlayState,
    MenuPurpose,
    TextInputOverlayState,
    TextInputPurpose,
)
from .texts import (
    DELETE_NOTE_TITLE,
    ERROR_EMPTY_NAME,
    ERROR_NOTE_NOT_FOUND,
    NEW_NOTE_MESSAGE,
    NEW_NOTE_TITLE,
    NOTE_MENU_TITLE,
    RENAME_NOTE_MESSAGE,
    RENAME_NOTE_TITLE,
    STATUS_NOTHING_TO_SAVE,
    note_edit_menu_options,
    note_list_menu_options,
)
from .utils import sanitize_title


class ControllerActionsMixin:
    def open_text_dialog(
        self,
        purpose: TextInputPurpose,
        title: str,
        initial: str = "",
        message: str = "",
    ) -> None:
        self.state.held_keys.clear()
        self.state.overlay = TextInputOverlayState(
            title=title,
            purpose=purpose,
            message=message,
            text=initial,
            cursor=len(initial),
        )
        self.state.shift = False
        if self.state.layout_id == "symbols_basic":
            self.layouts.switch_to_alpha()

    def open_menu_overlay(self, title: str, purpose: MenuPurpose, options) -> None:
        self.state.held_keys.clear()
        self.state.overlay = MenuOverlayState(title=title, purpose=purpose, options=list(options))

    def open_confirm_overlay(
        self,
        title: str,
        message: str,
        purpose: ConfirmPurpose,
        target: Path | None = None,
    ) -> None:
        self.state.held_keys.clear()
        self.state.overlay = ConfirmOverlayState(title=title, message=message, purpose=purpose, target=target)

    def open_note_menu(self) -> None:
        if self.state.mode in {AppMode.EDIT, AppMode.PREVIEW} and self.state.current_path:
            self.open_menu_overlay(
                NOTE_MENU_TITLE,
                MenuPurpose.NOTE_EDIT,
                note_edit_menu_options(include_save=True),
            )
        elif self.notes.current_selected_path():
            self.open_menu_overlay(
                NOTE_MENU_TITLE,
                MenuPurpose.NOTE_LIST,
                note_list_menu_options(),
            )

    def open_settings(self) -> None:
        self.state.held_keys.clear()
        self.state.mode = AppMode.SETTINGS
        self.state.overlay = None

    def close_overlay(self) -> None:
        self.clear_overlay()

    def confirm_text_dialog(self) -> None:
        if not isinstance(self.state.overlay, TextInputOverlayState):
            return
        text = sanitize_title(self.state.overlay.text)
        if not text:
            self.state.overlay.error = ERROR_EMPTY_NAME
            return

        if self.state.overlay.purpose == TextInputPurpose.NEW_NOTE:
            if self.notes.create_note(text):
                self.state.overlay = None
            return

        if self.state.overlay.purpose == TextInputPurpose.RENAME_NOTE:
            target = self.state.current_path if self.state.mode == AppMode.EDIT else self.notes.current_selected_path()
            if not target:
                self.state.overlay.error = ERROR_NOTE_NOT_FOUND
                return
            if self.notes.rename_note(target, text):
                self.state.overlay = None

    def handle_menu_confirm(self) -> None:
        if not isinstance(self.state.overlay, MenuOverlayState):
            return

        option = self.state.overlay.options[self.state.overlay.selected]
        action = option.action
        purpose = self.state.overlay.purpose

        if action == MenuAction.CANCEL:
            self.close_overlay()
            return

        target = self.state.current_path if self.state.mode == AppMode.EDIT else self.notes.current_selected_path()
        if self.state.mode == AppMode.PREVIEW and self.state.current_path:
            target = self.state.current_path

        if purpose in {MenuPurpose.NOTE_LIST, MenuPurpose.NOTE_EDIT}:
            if action == MenuAction.SAVE:
                if not self.state.current_path or not self.state.dirty:
                    self.flash_status(STATUS_NOTHING_TO_SAVE)
                else:
                    self.notes.save_dirty_note(force=True)
                self.close_overlay()
                return

            if not target:
                self.close_overlay()
                return

            if action == MenuAction.PREVIEW:
                self.close_overlay()
                self.editor.open_preview()
            elif action == MenuAction.RENAME:
                self.open_text_dialog(
                    TextInputPurpose.RENAME_NOTE,
                    RENAME_NOTE_TITLE,
                    target.stem,
                    RENAME_NOTE_MESSAGE,
                )
            elif action == MenuAction.DELETE:
                self.open_confirm_overlay(DELETE_NOTE_TITLE, target.stem, ConfirmPurpose.DELETE_NOTE, target=target)
            elif action == MenuAction.BACK:
                if self.notes.ensure_note_saved():
                    self.notes.refresh_notes()
                    self.state.mode = AppMode.LIST
                self.close_overlay()

    def handle_confirm_overlay(self) -> None:
        if not isinstance(self.state.overlay, ConfirmOverlayState):
            return

        option = self.state.overlay.options[self.state.overlay.selected]
        if option.action == MenuAction.CANCEL:
            self.close_overlay()
            return

        if self.state.overlay.purpose == ConfirmPurpose.DELETE_NOTE and self.state.overlay.target:
            self.notes.delete_note(self.state.overlay.target)
            self.close_overlay()

    def open_new_note_dialog(self) -> None:
        self.open_text_dialog(TextInputPurpose.NEW_NOTE, NEW_NOTE_TITLE, "", NEW_NOTE_MESSAGE)
