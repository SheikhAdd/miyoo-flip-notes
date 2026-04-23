from __future__ import annotations

import unittest

from notes.keyboard_geometry import move_selection, remap_selection


class KeyboardGeometryTests(unittest.TestCase):
    def test_vertical_move_uses_nearest_horizontal_position(self) -> None:
        rows = [
            list("abcdefghij"),
            ["one", "two", "three", "four", "five"],
        ]
        row, col = move_selection(rows, 0, 0, 0, 1)
        self.assertEqual((row, col), (1, 0))

    def test_vertical_move_from_end_targets_nearest_key(self) -> None:
        rows = [
            list("abcdefghij"),
            ["one", "two", "three", "four", "five"],
        ]
        row, col = move_selection(rows, 0, 9, 0, 1)
        self.assertEqual((row, col), (1, 4))

    def test_remap_selection_keeps_nearest_column_when_layout_changes(self) -> None:
        old_rows = [list("abcdefghij")]
        new_rows = [["left", "middle", "right"]]
        row, col = remap_selection(old_rows, new_rows, 0, 4)
        self.assertEqual((row, col), (0, 2))


if __name__ == "__main__":
    unittest.main()
