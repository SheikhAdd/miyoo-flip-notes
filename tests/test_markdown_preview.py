from __future__ import annotations

import unittest

from notes.markdown_preview import parse_markdown_blocks, plain_markdown_text
from notes.models import PreviewStyle


class MarkdownPreviewTests(unittest.TestCase):
    def test_plain_markdown_text_strips_basic_markup(self) -> None:
        self.assertEqual(plain_markdown_text("**hello** _world_ `x`"), "hello world x")

    def test_parse_markdown_blocks_detects_headers_and_bullets(self) -> None:
        blocks = parse_markdown_blocks("# Title\n- item\n> quote\n")
        self.assertEqual(blocks[0].style, PreviewStyle.H1)
        self.assertEqual(blocks[1].text, "- item")
        self.assertEqual(blocks[2].style, PreviewStyle.QUOTE)

    def test_parse_markdown_blocks_handles_fenced_code(self) -> None:
        blocks = parse_markdown_blocks("```py\nprint(1)\n```")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].style, PreviewStyle.CODE)


if __name__ == "__main__":
    unittest.main()
