from __future__ import annotations

import time

from .config_store import BUTTON_SCHEME_NAMES
from .models import (
    AppConfig,
    AppMode,
    ButtonScheme,
    ConfirmOverlayState,
    MenuAction,
    MenuOption,
    MenuOverlayState,
    TextInputOverlayState,
)


NOTES_TITLE = "Notes"
SETTINGS_TITLE = "Settings"
LAYOUTS_TITLE = "Layouts"
NOTE_MENU_TITLE = "Note menu"
NEW_NOTE_TITLE = "New note"
NEW_NOTE_MESSAGE = "Enter a note title."
RENAME_NOTE_TITLE = "Rename note"
RENAME_NOTE_MESSAGE = "Edit the note title."
DELETE_NOTE_TITLE = "Delete note?"
PREVIEW_BADGE = "Simple MD"
STATUS_BUTTON_SCHEME_SAVED = "Button scheme saved"
STATUS_LAYOUTS_UPDATED = "Layouts updated"
STATUS_NOTE_CREATED = "Note created"
STATUS_NOTE_RENAMED = "Note renamed"
STATUS_NOTE_DELETED = "Note deleted"
STATUS_NAME_UNCHANGED = "Name unchanged"
STATUS_NOTHING_TO_SAVE = "Nothing to save"
ERROR_EMPTY_NAME = "Name cannot be empty"
ERROR_NOTE_NOT_FOUND = "Note not found"
ERROR_SYMBOLS_LAYOUT_DISABLED = "Symbols layout is disabled"


def confirm_label(config: AppConfig) -> str:
    return "B" if config.button_scheme == ButtonScheme.STANDARD else "A"


def delete_label() -> str:
    return "Y"


def shift_label(config: AppConfig) -> str:
    return "A" if config.button_scheme == ButtonScheme.STANDARD else "B"


def space_label() -> str:
    return "X"


def footer_text(state) -> str:
    if time.monotonic() < state.flash_status_until:
        return state.flash_status_text

    confirm = confirm_label(state.config)
    delete = delete_label()
    shift = shift_label(state.config)
    space = space_label()

    if isinstance(state.overlay, TextInputOverlayState):
        return f"{confirm} Key  {delete} Delete  {space} Space  {shift} Shift  R2 Done  L2 Symbols  SELECT Cancel"
    if isinstance(state.overlay, (MenuOverlayState, ConfirmOverlayState)):
        return f"{confirm} Select  SELECT Cancel"

    if state.mode == AppMode.LIST:
        return f"{confirm} Open  {space} New  {shift} Note Menu  START Settings  SELECT Quit"
    if state.mode == AppMode.EDIT:
        return f"{confirm} Key  {delete} Delete  {space} Space  {shift} Shift  R2 Enter  L2 Symbols  START Note  SELECT Back"
    if state.mode == AppMode.PREVIEW:
        return "START Note Menu  SELECT Back  Right stick Scroll"
    if state.mode == AppMode.SETTINGS:
        return f"{confirm} Change  SELECT Back"
    if state.mode == AppMode.LAYOUTS:
        return f"{confirm} Toggle  SELECT Back"
    return ""


def button_scheme_name(config: AppConfig) -> str:
    return BUTTON_SCHEME_NAMES[config.button_scheme]


def settings_rows(config: AppConfig) -> list[tuple[str, str]]:
    return [
        ("Primary buttons", button_scheme_name(config)),
        ("Autosave", "Enabled" if config.autosave_enabled else "Disabled"),
        ("Autosave interval", f"{config.autosave_minutes} min"),
        ("Text size", f"{config.text_scale_percent}%"),
        ("Keyboard layouts", "Enable or disable built-in layouts"),
        ("Back to notes", "Return to the note list"),
    ]


def note_edit_menu_options(include_save: bool) -> list[MenuOption]:
    options: list[MenuOption] = []
    if include_save:
        options.append(MenuOption(MenuAction.SAVE, "Save"))
    options.extend(
        [
            MenuOption(MenuAction.PREVIEW, "Simple Preview"),
            MenuOption(MenuAction.RENAME, "Rename"),
            MenuOption(MenuAction.DELETE, "Delete"),
            MenuOption(MenuAction.BACK, "Back to list"),
            MenuOption(MenuAction.CANCEL, "Cancel"),
        ]
    )
    return options


def note_list_menu_options() -> list[MenuOption]:
    return [
        MenuOption(MenuAction.PREVIEW, "Simple Preview"),
        MenuOption(MenuAction.RENAME, "Rename"),
        MenuOption(MenuAction.DELETE, "Delete"),
        MenuOption(MenuAction.CANCEL, "Cancel"),
    ]


def autosave_status(enabled: bool) -> str:
    return "Autosave enabled" if enabled else "Autosave disabled"


def autosave_interval_status(minutes: int) -> str:
    return f"Autosave every {minutes} min"


def text_scale_status(percent: int) -> str:
    return f"Text size {percent}%"


def save_status(force: bool, timestamp: str) -> str:
    return ("Saved " if force else "Autosaved ") + timestamp


def settings_save_error(exc: OSError) -> str:
    return f"Could not save settings: {exc}"
