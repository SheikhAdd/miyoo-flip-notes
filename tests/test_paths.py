from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from notes.paths import resolve_runtime_paths


class PathsTests(unittest.TestCase):
    def test_env_overrides_are_applied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = {
                "NOTES_DIR": str(Path(tmp_dir) / "notes-data"),
                "NOTES_SDL_EXLIBS": str(Path(tmp_dir) / "exlibs"),
                "NOTES_SDL_DLL_PATH": str(Path(tmp_dir) / "dlls"),
                "NOTES_FONT_UI": str(Path(tmp_dir) / "ui.ttf"),
                "NOTES_FONT_MONO": str(Path(tmp_dir) / "mono.ttf"),
            }

            paths = resolve_runtime_paths(environ=env, app_root=Path(tmp_dir) / "app")

            self.assertEqual(paths.data_dir, Path(tmp_dir) / "notes-data")
            self.assertEqual(paths.sdl_exlibs, Path(tmp_dir) / "exlibs")
            self.assertEqual(paths.sdl_dll_path, str(Path(tmp_dir) / "dlls"))
            self.assertEqual(paths.font_ui, Path(tmp_dir) / "ui.ttf")
            self.assertEqual(paths.font_mono, Path(tmp_dir) / "mono.ttf")


if __name__ == "__main__":
    unittest.main()
