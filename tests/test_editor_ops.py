from __future__ import annotations

import unittest

from notes.editor_ops import delete_backward, insert_text, move_line_end, move_line_start, move_vertical


class EditorOpsTests(unittest.TestCase):
    def test_insert_text_updates_cursor(self) -> None:
        text, cursor = insert_text("ab", 1, "X")
        self.assertEqual(text, "aXb")
        self.assertEqual(cursor, 2)

    def test_delete_backward_updates_cursor(self) -> None:
        text, cursor = delete_backward("abcd", 3)
        self.assertEqual(text, "abd")
        self.assertEqual(cursor, 2)

    def test_move_line_bounds(self) -> None:
        text = "abc\ndef"
        self.assertEqual(move_line_start(text, 5), 4)
        self.assertEqual(move_line_end(text, 1), 3)

    def test_move_vertical_preserves_column_when_possible(self) -> None:
        text = "1234567890\nabc\n12345"
        cursor = 8
        moved = move_vertical(text, cursor, 5, 1)
        self.assertEqual(moved, 11)


if __name__ == "__main__":
    unittest.main()
