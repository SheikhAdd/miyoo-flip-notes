from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AppMode(str, Enum):
    LIST = "list"
    EDIT = "edit"
    PREVIEW = "preview"
    SETTINGS = "settings"
    LAYOUTS = "layouts"


class ButtonScheme(str, Enum):
    STANDARD = "standard"
    SWAPPED = "swapped"


class LayoutFamily(str, Enum):
    ALPHA = "alpha"
    SYMBOLS = "symbols"


class PreviewStyle(str, Enum):
    BODY = "body"
    H1 = "h1"
    H2 = "h2"
    QUOTE = "quote"
    META = "meta"
    CODE = "code"


class MenuPurpose(str, Enum):
    NOTE_LIST = "note_menu_list"
    NOTE_EDIT = "note_menu_edit"


class MenuAction(str, Enum):
    SAVE = "save"
    PREVIEW = "preview"
    RENAME = "rename"
    DELETE = "delete"
    BACK = "back"
    CONFIRM = "confirm"
    CANCEL = "cancel"


class ConfirmPurpose(str, Enum):
    DELETE_NOTE = "delete_note"


class TextInputPurpose(str, Enum):
    NEW_NOTE = "new_note"
    RENAME_NOTE = "rename_note"


@dataclass(frozen=True)
class KeyboardLayout:
    layout_id: str
    title: str
    short: str
    family: LayoutFamily
    rows: list[list[str]]


@dataclass
class AppConfig:
    button_scheme: ButtonScheme = ButtonScheme.STANDARD
    active_layouts: list[str] = field(default_factory=list)
    autosave_enabled: bool = False
    autosave_minutes: int = 5
    text_scale_percent: int = 100


@dataclass(frozen=True)
class PreviewBlock:
    text: str
    style: PreviewStyle
    indent: int


@dataclass(frozen=True)
class PreviewLine:
    text: str
    style: PreviewStyle
    indent: int
    height: int


@dataclass(frozen=True)
class NoteRecord:
    path: Path
    title: str
    modified_at: float


@dataclass(frozen=True)
class MenuOption:
    action: MenuAction
    label: str


@dataclass
class MenuOverlayState:
    title: str
    purpose: MenuPurpose
    options: list[MenuOption]
    selected: int = 0


@dataclass
class ConfirmOverlayState:
    title: str
    message: str
    purpose: ConfirmPurpose
    target: Path | None = None
    selected: int = 0
    options: list[MenuOption] = field(
        default_factory=lambda: [
            MenuOption(MenuAction.CONFIRM, "Delete"),
            MenuOption(MenuAction.CANCEL, "Cancel"),
        ]
    )


@dataclass
class TextInputOverlayState:
    title: str
    purpose: TextInputPurpose
    message: str = ""
    text: str = ""
    cursor: int = 0
    error: str = ""


OverlayState = MenuOverlayState | ConfirmOverlayState | TextInputOverlayState


@dataclass
class AppState:
    mode: AppMode = AppMode.LIST
    overlay: OverlayState | None = None
    notes: list[NoteRecord] = field(default_factory=list)
    selected_note: int = 0
    list_scroll: int = 0
    settings_index: int = 0
    layouts_index: int = 0
    layouts_scroll: int = 0
    current_path: Path | None = None
    text: str = ""
    cursor: int = 0
    text_scroll: int = 0
    follow_cursor: bool = True
    dirty: bool = False
    last_save_at: float = 0.0
    config: AppConfig = field(default_factory=AppConfig)
    layout_id: str = ""
    previous_layout_id: str = ""
    shift: bool = False
    key_row: int = 0
    key_col: int = 0
    preview_title: str = ""
    preview_lines: list[PreviewLine] = field(default_factory=list)
    preview_scroll: int = 0
    preview_return_mode: AppMode = AppMode.LIST
    held_keys: dict[int, float] = field(default_factory=dict)
    repeat_delay: float = 0.38
    repeat_interval: float = 0.045
    flash_status_text: str = ""
    flash_status_until: float = 0.0
    char_width: int = 10
    line_height: int = 20

