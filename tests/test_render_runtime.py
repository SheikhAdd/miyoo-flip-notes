from __future__ import annotations

import unittest
from unittest.mock import patch

from notes.render import set_video_hints


class FakeSdl:
    SDL_HINT_RENDER_SCALE_QUALITY = b"SDL_RENDER_SCALE_QUALITY"
    SDL_HINT_WINDOWS_DPI_AWARENESS = b"SDL_WINDOWS_DPI_AWARENESS"

    def __init__(self) -> None:
        self.calls: list[tuple[bytes, bytes]] = []

    def SDL_SetHint(self, name, value) -> None:
        self.calls.append((name, value))


class RenderRuntimeTests(unittest.TestCase):
    def test_set_video_hints_enables_nearest_scaling(self) -> None:
        sdl = FakeSdl()

        set_video_hints(sdl)

        self.assertIn((sdl.SDL_HINT_RENDER_SCALE_QUALITY, b"0"), sdl.calls)

    def test_set_video_hints_requests_windows_dpi_awareness_on_windows(self) -> None:
        sdl = FakeSdl()

        with patch("notes.render.os.name", "nt"):
            set_video_hints(sdl)

        self.assertIn((sdl.SDL_HINT_WINDOWS_DPI_AWARENESS, b"permonitorv2"), sdl.calls)


if __name__ == "__main__":
    unittest.main()
