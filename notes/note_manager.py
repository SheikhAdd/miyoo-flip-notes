from __future__ import annotations

import time
from pathlib import Path

from .constants import LIST_VISIBLE_ROWS
from .models import AppMode, AppState, NoteRecord
from .storage import NoteRepository, StorageError
from .texts import STATUS_NAME_UNCHANGED, STATUS_NOTE_CREATED, STATUS_NOTE_DELETED, STATUS_NOTE_RENAMED, save_status
from .utils import clamp


class NoteManager:
    def __init__(self, state: AppState, repository: NoteRepository, flash_status) -> None:
        self.state = state
        self.repository = repository
        self.flash_status = flash_status

    def current_selected_record(self) -> NoteRecord | None:
        if not self.state.notes:
            return None
        index = clamp(self.state.selected_note, 0, len(self.state.notes) - 1)
        return self.state.notes[index]

    def current_selected_path(self) -> Path | None:
        record = self.current_selected_record()
        return record.path if record else None

    def ensure_note_visible(self) -> None:
        if self.state.selected_note < self.state.list_scroll:
            self.state.list_scroll = self.state.selected_note
        elif self.state.selected_note >= self.state.list_scroll + LIST_VISIBLE_ROWS:
            self.state.list_scroll = self.state.selected_note - LIST_VISIBLE_ROWS + 1
        self.state.list_scroll = max(0, min(self.state.list_scroll, max(0, len(self.state.notes) - LIST_VISIBLE_ROWS)))

    def refresh_notes(self) -> None:
        selected = self.current_selected_path()
        try:
            self.state.notes = self.repository.list_notes()
        except StorageError as exc:
            self.flash_status(str(exc))
            self.state.notes = []
            return
        if not self.state.notes:
            try:
                self.repository.ensure_welcome_note()
                self.state.notes = self.repository.list_notes()
            except StorageError as exc:
                self.flash_status(str(exc))
                self.state.notes = []
                return
        note_paths = [record.path for record in self.state.notes]
        if selected and selected in note_paths:
            self.state.selected_note = note_paths.index(selected)
        else:
            self.state.selected_note = clamp(self.state.selected_note, 0, max(0, len(self.state.notes) - 1))
        self.ensure_note_visible()

    def create_note(self, title: str) -> bool:
        try:
            path = self.repository.create_note(title)
        except StorageError as exc:
            self.flash_status(str(exc))
            return False
        self.refresh_notes()
        note_paths = [record.path for record in self.state.notes]
        if path in note_paths:
            self.state.selected_note = note_paths.index(path)
        if not self.open_note(path):
            return False
        self.flash_status(STATUS_NOTE_CREATED)
        return True

    def rename_note(self, source: Path, new_title: str) -> bool:
        if self.state.current_path == source and self.state.dirty:
            if not self.save_dirty_note(True):
                return False
        try:
            target = self.repository.rename_note(source, new_title)
        except StorageError as exc:
            self.flash_status(str(exc))
            return False
        if target == source:
            self.flash_status(STATUS_NAME_UNCHANGED)
            return True
        if self.state.current_path == source:
            self.state.current_path = target
            self.state.preview_title = target.stem
        self.refresh_notes()
        note_paths = [record.path for record in self.state.notes]
        if target in note_paths:
            self.state.selected_note = note_paths.index(target)
        self.flash_status(STATUS_NOTE_RENAMED)
        return True

    def delete_note(self, path: Path) -> bool:
        try:
            self.repository.delete_note(path)
        except StorageError as exc:
            self.flash_status(str(exc))
            return False
        if self.state.current_path == path:
            self.state.current_path = None
            self.state.text = ""
            self.state.cursor = 0
            self.state.mode = AppMode.LIST
        self.refresh_notes()
        self.flash_status(STATUS_NOTE_DELETED)
        return True

    def ensure_note_saved(self) -> bool:
        if self.state.current_path and self.state.dirty:
            return self.save_dirty_note(True)
        return True

    def open_note(self, path: Path) -> bool:
        if not self.ensure_note_saved():
            return False
        self.state.held_keys.clear()
        try:
            text = self.repository.read_note(path) if path.exists() else ""
        except StorageError as exc:
            self.flash_status(str(exc))
            return False
        self.state.current_path = path
        self.state.text = text
        self.state.cursor = len(text)
        self.state.text_scroll = 0
        self.state.follow_cursor = True
        self.state.dirty = False
        self.state.mode = AppMode.EDIT
        self.state.overlay = None
        self.state.shift = False
        return True

    def save_dirty_note(self, force: bool) -> bool:
        if not self.state.current_path or not self.state.dirty:
            return True
        now = time.monotonic()
        if not force:
            if not self.state.config.autosave_enabled:
                return True
            interval_seconds = max(60, int(self.state.config.autosave_minutes) * 60)
            if now - self.state.last_save_at < interval_seconds:
                return True
        try:
            self.repository.write_note_atomic(self.state.current_path, self.state.text)
        except StorageError as exc:
            self.flash_status(str(exc))
            return False
        self.state.dirty = False
        self.state.last_save_at = now
        self.refresh_notes()
        self.flash_status(save_status(force, time.strftime("%H:%M:%S")))
        return True
