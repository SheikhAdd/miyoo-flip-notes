from __future__ import annotations

import unittest

from notes.viewports import clamp_scroll, fit_cursor_window


class ViewportTests(unittest.TestCase):
    def test_clamp_scroll_follows_cursor_without_mutating_render_layer(self) -> None:
        self.assertEqual(clamp_scroll(current_scroll=0, cursor_line=6, total_lines=10, visible_rows=4, follow_cursor=True), 3)

    def test_clamp_scroll_preserves_scroll_when_follow_is_disabled(self) -> None:
        self.assertEqual(clamp_scroll(current_scroll=2, cursor_line=7, total_lines=10, visible_rows=4, follow_cursor=False), 2)

    def test_fit_cursor_window_keeps_cursor_visible_at_end_of_long_text(self) -> None:
        visible, cursor_offset = fit_cursor_window("abcdefghij", 10, 5, len)
        self.assertEqual(visible, "fghij")
        self.assertEqual(cursor_offset, 5)

    def test_fit_cursor_window_keeps_cursor_visible_in_middle(self) -> None:
        visible, cursor_offset = fit_cursor_window("abcdefghij", 4, 5, len)
        self.assertEqual(visible, "abcde")
        self.assertEqual(cursor_offset, 4)


if __name__ == "__main__":
    unittest.main()
