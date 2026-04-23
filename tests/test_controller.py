from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from notes.config_store import ConfigStore
from notes.controller import NotesController
from notes.layouts import get_layout
from notes.models import AppMode, ButtonScheme, TextInputOverlayState
from notes.storage import NoteRepository


class FakeUi:
    def refresh_text_font(self, text_scale_percent: int) -> tuple[int, int]:
        return (10, 20)

    def build_preview(self, markdown: str):
        return []

    def cleanup(self) -> None:
        pass


class FakeSdl:
    SDLK_ESCAPE = 1
    SDLK_RCTRL = 2
    SDLK_LCTRL = 3
    SDLK_LALT = 4
    SDLK_RETURN = 5
    SDLK_KP_ENTER = 6
    SDLK_BACKSPACE = 7
    SDLK_TAB = 8
    SDLK_F1 = 9
    SDLK_HOME = 10
    SDLK_END = 11
    SDLK_UP = 12
    SDLK_DOWN = 13
    SDLK_LEFT = 14
    SDLK_RIGHT = 15
    SDLK_INSERT = 16
    SDLK_DELETE = 17
    SDLK_PAGEUP = 18
    SDLK_PAGEDOWN = 19


class ControllerTests(unittest.TestCase):
    def make_controller(self) -> NotesController:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        data_dir = Path(tmp_dir.name)
        config_path = data_dir / "settings.json"
        return NotesController(
            ui=FakeUi(),
            sdl2_module=FakeSdl,
            config_store=ConfigStore(config_path=config_path, data_dir=data_dir),
            repository=NoteRepository(data_dir),
        )

    def test_symbols_toggle_returns_to_previous_layout(self) -> None:
        controller = self.make_controller()
        controller.state.layout_id = "ru_jcuken"
        controller.state.previous_layout_id = "ru_jcuken"
        controller.layouts.switch_to_symbols()
        self.assertEqual(controller.state.layout_id, "symbols_basic")
        controller.layouts.toggle_symbols_layout()
        self.assertEqual(controller.state.layout_id, "ru_jcuken")

    def test_open_note_menu_in_edit_mode_contains_save(self) -> None:
        controller = self.make_controller()
        path = controller.repository.create_note("Menu")
        controller.notes.open_note(path)
        controller.open_note_menu()
        self.assertEqual(controller.state.mode, AppMode.EDIT)
        self.assertIsNotNone(controller.state.overlay)
        labels = [option.label for option in controller.state.overlay.options]
        self.assertIn("Save", labels)

    def test_open_new_note_dialog_uses_overlay_model(self) -> None:
        controller = self.make_controller()
        controller.open_new_note_dialog()
        self.assertIsInstance(controller.state.overlay, TextInputOverlayState)

    def test_toggle_button_scheme_uses_neutral_values(self) -> None:
        controller = self.make_controller()
        self.assertEqual(controller.state.config.button_scheme, ButtonScheme.STANDARD)
        controller.settings.toggle_button_scheme()
        self.assertEqual(controller.state.config.button_scheme, ButtonScheme.SWAPPED)

    def test_apply_layout_preserves_nearest_position(self) -> None:
        controller = self.make_controller()
        controller.state.layout_id = "en_qwerty"
        controller.state.key_row = 0
        controller.state.key_col = len(get_layout("en_qwerty").rows[0]) - 1
        controller.layouts.apply_layout("symbols_basic")
        self.assertEqual(controller.state.key_row, 0)
        self.assertGreaterEqual(controller.state.key_col, 0)

    def test_prepare_frame_updates_text_scroll_before_render(self) -> None:
        controller = self.make_controller()
        path = controller.repository.create_note("Viewport")
        controller.notes.open_note(path)
        controller.state.text = "abcdefghijklmnopqrstuvwxyz" * 6
        controller.state.cursor = len(controller.state.text)
        controller.state.char_width = 50
        controller.state.line_height = 20

        controller.editor.prepare_frame()

        self.assertGreater(controller.state.text_scroll, 0)

    def test_autosave_respects_interval_when_not_forced(self) -> None:
        controller = self.make_controller()
        path = controller.repository.create_note("Autosave")
        controller.notes.open_note(path)
        controller.state.text = "changed"
        controller.state.dirty = True
        controller.state.config.autosave_enabled = True
        controller.state.config.autosave_minutes = 1
        controller.state.last_save_at = time.monotonic()

        saved = controller.notes.save_dirty_note(force=False)

        self.assertTrue(saved)
        self.assertTrue(controller.state.dirty)
        self.assertEqual(controller.repository.read_note(path), "")


if __name__ == "__main__":
    unittest.main()
