from __future__ import annotations

import time
from typing import Protocol

from .config_store import ConfigStore
from .controller_actions import ControllerActionsMixin
from .controller_input import ControllerInputMixin
from .editor_controller import EditorController
from .layout_manager import LayoutManager
from .models import AppState, PreviewLine
from .note_manager import NoteManager
from .settings_manager import SettingsManager
from .storage import NoteRepository


class SupportsNotesUi(Protocol):
    def refresh_text_font(self, text_scale_percent: int) -> tuple[int, int]: ...

    def build_preview(self, markdown: str) -> list[PreviewLine]: ...

    def cleanup(self) -> None: ...


class NotesController(ControllerInputMixin, ControllerActionsMixin):
    def __init__(
        self,
        ui: SupportsNotesUi,
        sdl2_module,
        config_store: ConfigStore | None = None,
        repository: NoteRepository | None = None,
    ) -> None:
        self.ui = ui
        self.sdl2 = sdl2_module
        self.config_store = config_store or ConfigStore()
        self.repository = repository or NoteRepository()

        config = self.config_store.load()
        initial_layout = config.active_layouts[0]
        self.state = AppState(
            config=config,
            layout_id=initial_layout,
            previous_layout_id=initial_layout,
        )

        self.notes = NoteManager(self.state, self.repository, self.flash_status)
        self.layouts = LayoutManager(self.state, self.flash_status)
        self.settings = SettingsManager(
            self.state,
            self.config_store,
            self.layouts,
            self.ui,
            self.flash_status,
        )
        self.editor = EditorController(
            self.state,
            self.ui,
            self.repository,
            self.notes,
            self.layouts,
            self.flash_status,
            self.confirm_text_dialog,
        )

    def flash_status(self, message: str, seconds: float = 2.4) -> None:
        self.state.flash_status_text = message
        self.state.flash_status_until = time.monotonic() + seconds

    def clear_overlay(self) -> None:
        self.state.held_keys.clear()
        self.state.overlay = None

    def prepare_shutdown(self) -> bool:
        return self.notes.ensure_note_saved()

    def cleanup(self) -> bool:
        saved = self.notes.ensure_note_saved()
        self.ui.cleanup()
        return saved
