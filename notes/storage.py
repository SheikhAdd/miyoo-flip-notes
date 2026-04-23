from __future__ import annotations

from pathlib import Path

from .models import NoteRecord
from .paths import RuntimePaths, resolve_runtime_paths
from .utils import sanitize_title


class StorageError(RuntimeError):
    pass


class NoteRepository:
    def __init__(self, data_dir: Path | None = None, runtime_paths: RuntimePaths | None = None) -> None:
        resolved_paths = runtime_paths or resolve_runtime_paths()
        self.data_dir = data_dir or resolved_paths.data_dir

    def ensure_data_dir(self) -> None:
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(f"Could not prepare notes directory: {exc}") from exc

    def list_notes(self) -> list[NoteRecord]:
        self.ensure_data_dir()
        try:
            records = [
                NoteRecord(path=path, title=path.stem, modified_at=path.stat().st_mtime)
                for path in self.data_dir.iterdir()
                if path.is_file() and path.suffix.lower() in {".md", ".txt"}
            ]
        except OSError as exc:
            raise StorageError(f"Could not read notes: {exc}") from exc
        return sorted(records, key=lambda record: record.modified_at, reverse=True)

    def ensure_welcome_note(self) -> Path:
        self.ensure_data_dir()
        welcome = self.data_dir / "Quick Note.md"
        if welcome.exists():
            return welcome
        try:
            welcome.write_text("# Quick Note\n\nType something.\n", encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not create welcome note: {exc}") from exc
        return welcome

    def unique_note_path(self, title: str, suffix: str = ".md", exclude: Path | None = None) -> Path:
        stem = sanitize_title(title) or "Untitled"
        candidate = self.data_dir / f"{stem}{suffix}"
        index = 2
        while candidate.exists() and candidate != exclude:
            candidate = self.data_dir / f"{stem} ({index}){suffix}"
            index += 1
        return candidate

    def create_note(self, title: str) -> Path:
        self.ensure_data_dir()
        path = self.unique_note_path(title)
        try:
            path.write_text("", encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not create note: {exc}") from exc
        return path

    def rename_note(self, source: Path, new_title: str) -> Path:
        if not source.exists():
            raise StorageError("Note file is missing")
        cleaned = sanitize_title(new_title)
        if not cleaned:
            raise StorageError("Name cannot be empty")
        target = self.unique_note_path(cleaned, source.suffix, exclude=source)
        if target == source:
            return source
        try:
            source.rename(target)
        except OSError as exc:
            raise StorageError(f"Could not rename note: {exc}") from exc
        return target

    def delete_note(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            path.unlink()
        except OSError as exc:
            raise StorageError(f"Could not delete note: {exc}") from exc

    def read_note(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise StorageError(f"Could not read note: {exc}") from exc

    def write_note_atomic(self, path: Path, text: str) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(path)
        except OSError as exc:
            raise StorageError(f"Could not save note: {exc}") from exc
