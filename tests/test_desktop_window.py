from __future__ import annotations

import unittest

from notes.constants import LOGICAL_HEIGHT, LOGICAL_WIDTH
from notes.desktop_window import parse_window_scale, resolve_window_config


class DesktopWindowTests(unittest.TestCase):
    def test_default_window_mode_is_fullscreen(self) -> None:
        config = resolve_window_config({})

        self.assertEqual(config.mode, "fullscreen")
        self.assertEqual(config.width, LOGICAL_WIDTH)
        self.assertEqual(config.height, LOGICAL_HEIGHT)
        self.assertTrue(config.fullscreen)

    def test_windowed_mode_scales_logical_size(self) -> None:
        config = resolve_window_config({"NOTES_WINDOW_MODE": "windowed", "NOTES_WINDOW_SCALE": "3"})

        self.assertEqual(config.mode, "windowed")
        self.assertEqual(config.width, LOGICAL_WIDTH * 3)
        self.assertEqual(config.height, LOGICAL_HEIGHT * 3)
        self.assertFalse(config.fullscreen)

    def test_invalid_window_scale_falls_back_to_default(self) -> None:
        self.assertEqual(parse_window_scale("bad"), 2)
        self.assertEqual(parse_window_scale("-10"), 1)
        self.assertEqual(parse_window_scale("99"), 6)


if __name__ == "__main__":
    unittest.main()
