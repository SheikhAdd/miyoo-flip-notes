from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from notes.storage import NoteRepository


class StorageTests(unittest.TestCase):
    def test_create_rename_delete_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = NoteRepository(Path(tmp_dir))
            path = repo.create_note("Test")
            self.assertTrue(path.exists())

            renamed = repo.rename_note(path, "Renamed")
            self.assertTrue(renamed.exists())
            self.assertEqual(renamed.stem, "Renamed")

            repo.delete_note(renamed)
            self.assertFalse(renamed.exists())

    def test_ensure_welcome_note_creates_default_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = NoteRepository(Path(tmp_dir))
            welcome = repo.ensure_welcome_note()
            self.assertTrue(welcome.exists())
            self.assertIn("Quick Note", repo.read_note(welcome))


if __name__ == "__main__":
    unittest.main()

