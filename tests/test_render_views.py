from __future__ import annotations

import unittest
from pathlib import Path

from notes.editor_ops import visual_lines
from notes.layouts import DEFAULT_LAYOUT_IDS
from notes.models import (
    AppMode,
    AppState,
    ConfirmOverlayState,
    ConfirmPurpose,
    MenuAction,
    MenuOption,
    MenuOverlayState,
    MenuPurpose,
    PreviewLine,
    PreviewStyle,
    TextInputOverlayState,
    TextInputPurpose,
)
from notes.render_views import RenderViewsMixin


class FakeSdl:
    def SDL_RenderPresent(self, renderer) -> None:
        pass


class FakeRenderer(RenderViewsMixin):
    def __init__(self) -> None:
        self.sdl2 = FakeSdl()
        self.renderer = object()
        self.font_title = object()
        self.font_ui = object()
        self.font_small = object()
        self.font_text = object()
        self.font_key = object()

    def fill_rect(self, *args) -> None:
        pass

    def draw_text(self, *args) -> None:
        pass

    def draw_panel(self, *args) -> None:
        pass

    def measure(self, text: str, font) -> tuple[int, int]:
        return (len(text) * 8, 16)

    def wrap_text(self, text: str, font, max_width: int) -> list[str]:
        return [text] if text else [""]

    def preview_font(self, style):
        return self.font_text

    def preview_color(self, style):
        return (255, 255, 255, 255)

    def visual_lines(self, text: str, cursor: int, max_cols: int) -> tuple[list[str], int, int]:
        return visual_lines(text, cursor, max_cols)


class RenderViewsTests(unittest.TestCase):
    def make_state(self, **overrides) -> AppState:
        state = AppState(layout_id=DEFAULT_LAYOUT_IDS[0], previous_layout_id=DEFAULT_LAYOUT_IDS[0])
        for key, value in overrides.items():
            setattr(state, key, value)
        return state

    def test_render_smoke_for_all_main_modes(self) -> None:
        renderer = FakeRenderer()

        states = [
            self.make_state(mode=AppMode.LIST),
            self.make_state(mode=AppMode.EDIT, current_path=Path("Quick Note.md"), text="hello", cursor=5),
            self.make_state(
                mode=AppMode.PREVIEW,
                preview_title="Quick Note",
                preview_lines=[PreviewLine("hello", PreviewStyle.BODY, 0, 18)],
            ),
            self.make_state(mode=AppMode.SETTINGS),
            self.make_state(mode=AppMode.LAYOUTS),
        ]

        for state in states:
            renderer.render(state)

    def test_render_smoke_for_all_overlay_types(self) -> None:
        renderer = FakeRenderer()

        overlays = [
            MenuOverlayState(
                title="Menu",
                purpose=MenuPurpose.NOTE_LIST,
                options=[MenuOption(MenuAction.SAVE, "Save"), MenuOption(MenuAction.BACK, "Back")],
            ),
            ConfirmOverlayState(
                title="Delete note",
                message="Delete this note?",
                purpose=ConfirmPurpose.DELETE_NOTE,
            ),
            TextInputOverlayState(
                title="Rename note",
                purpose=TextInputPurpose.RENAME_NOTE,
                message="Enter a note name",
                text="Quick Note",
                cursor=5,
            ),
        ]

        for overlay in overlays:
            renderer.render(self.make_state(mode=AppMode.EDIT, overlay=overlay, current_path=Path("Quick Note.md"), text="body"))


if __name__ == "__main__":
    unittest.main()
