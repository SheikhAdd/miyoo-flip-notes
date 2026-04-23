from __future__ import annotations

import os
import sys
from ctypes import byref, c_int

from .constants import (
    COLOR_PANEL_3,
    COLOR_TEXT,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
)
from .desktop_window import resolve_window_config
from .editor_ops import visual_lines
from .markdown_preview import parse_markdown_blocks, plain_markdown_text
from .models import PreviewLine, PreviewStyle
from .paths import RuntimePaths, resolve_runtime_paths
from .render_views import RenderViewsMixin


def import_sdl_modules():
    import sdl2  # type: ignore
    import sdl2.sdlttf as sdlttf  # type: ignore

    return sdl2, sdlttf


def load_sdl(runtime_paths: RuntimePaths):
    try:
        return import_sdl_modules()
    except ModuleNotFoundError:
        if runtime_paths.sdl_exlibs.exists() and str(runtime_paths.sdl_exlibs) not in sys.path:
            sys.path.insert(0, str(runtime_paths.sdl_exlibs))
        os.environ.setdefault("PYSDL2_DLL_PATH", runtime_paths.sdl_dll_path)
        try:
            return import_sdl_modules()
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Could not import SDL2. Set NOTES_SDL_EXLIBS/NOTES_SDL_DLL_PATH or install PySDL2 locally."
            ) from exc


def sdl_color(sdl2, color: tuple[int, int, int, int]):
    return sdl2.SDL_Color(color[0], color[1], color[2], color[3])


def c_text(value: str) -> bytes:
    return value.encode("utf-8", "replace")


def set_video_hints(sdl2) -> None:
    set_hint = getattr(sdl2, "SDL_SetHint", None)
    if set_hint is None:
        return

    render_scale_quality = getattr(sdl2, "SDL_HINT_RENDER_SCALE_QUALITY", None)
    if render_scale_quality is not None:
        set_hint(render_scale_quality, c_text("0"))

    windows_dpi_awareness = getattr(sdl2, "SDL_HINT_WINDOWS_DPI_AWARENESS", None)
    if os.name == "nt" and windows_dpi_awareness is not None:
        set_hint(windows_dpi_awareness, c_text("permonitorv2"))


class NotesUi(RenderViewsMixin):
    def __init__(self, runtime_paths: RuntimePaths | None = None) -> None:
        self.paths = runtime_paths or resolve_runtime_paths()
        self.sdl2, self.sdlttf = load_sdl(self.paths)
        self.window = None
        self.renderer = None
        self.font_title = None
        self.font_ui = None
        self.font_small = None
        self.font_text = None
        self.font_key = None
        self.text_font_path = self.paths.font_mono if self.paths.font_mono.exists() else self.paths.font_ui
        self.sdl_ready = False
        self.ttf_ready = False
        self.text_input_started = False

    def init_sdl(self) -> None:
        set_video_hints(self.sdl2)
        if self.sdl2.SDL_Init(self.sdl2.SDL_INIT_VIDEO | self.sdl2.SDL_INIT_EVENTS) != 0:
            raise RuntimeError(self.sdl2.SDL_GetError().decode("utf-8", "ignore"))
        self.sdl_ready = True
        if self.sdlttf.TTF_Init() != 0:
            raise RuntimeError(self.sdl2.SDL_GetError().decode("utf-8", "ignore"))
        self.ttf_ready = True

        window_config = resolve_window_config(os.environ)
        flags = self.sdl2.SDL_WINDOW_SHOWN
        flags |= getattr(self.sdl2, "SDL_WINDOW_ALLOW_HIGHDPI", 0)
        if window_config.fullscreen:
            flags |= self.sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        self.window = self.sdl2.SDL_CreateWindow(
            b"Notes",
            self.sdl2.SDL_WINDOWPOS_CENTERED,
            self.sdl2.SDL_WINDOWPOS_CENTERED,
            window_config.width,
            window_config.height,
            flags,
        )
        if not self.window:
            raise RuntimeError(self.sdl2.SDL_GetError().decode("utf-8", "ignore"))

        self.renderer = self.sdl2.SDL_CreateRenderer(
            self.window,
            -1,
            self.sdl2.SDL_RENDERER_ACCELERATED | self.sdl2.SDL_RENDERER_PRESENTVSYNC,
        )
        if not self.renderer:
            self.renderer = self.sdl2.SDL_CreateRenderer(self.window, -1, self.sdl2.SDL_RENDERER_SOFTWARE)
        if not self.renderer:
            raise RuntimeError(self.sdl2.SDL_GetError().decode("utf-8", "ignore"))
        self.sdl2.SDL_SetRenderDrawBlendMode(self.renderer, self.sdl2.SDL_BLENDMODE_BLEND)
        if hasattr(self.sdl2, "SDL_RenderSetIntegerScale"):
            self.sdl2.SDL_RenderSetIntegerScale(self.renderer, getattr(self.sdl2, "SDL_TRUE", 1))
        if self.sdl2.SDL_RenderSetLogicalSize(self.renderer, LOGICAL_WIDTH, LOGICAL_HEIGHT) != 0:
            raise RuntimeError(self.sdl2.SDL_GetError().decode("utf-8", "ignore"))

        ui_font = self.paths.font_ui if self.paths.font_ui.exists() else self.paths.font_mono
        text_font = self.paths.font_mono if self.paths.font_mono.exists() else ui_font
        self.text_font_path = text_font
        self.font_title = self.open_font(ui_font, 22)
        self.font_ui = self.open_font(ui_font, 16)
        self.font_small = self.open_font(ui_font, 12)
        self.font_key = self.open_font(ui_font, 15)
        self.refresh_text_font(100)
        self.sdl2.SDL_StartTextInput()
        self.text_input_started = True

    def open_font(self, path, size: int):
        font = self.sdlttf.TTF_OpenFont(str(path).encode(), size)
        if not font:
            raise RuntimeError(f"Could not open font: {path}")
        return font

    def refresh_text_font(self, text_scale_percent: int) -> tuple[int, int]:
        size = max(12, int(round(16 * int(text_scale_percent) / 100)))
        if self.font_text:
            self.sdlttf.TTF_CloseFont(self.font_text)
        self.font_text = self.open_font(self.text_font_path, size)
        char_width = max(7, self.measure("M", self.font_text)[0])
        line_height = max(18, self.measure("M", self.font_text)[1] + 4)
        return (char_width, line_height)

    def cleanup(self) -> None:
        if self.text_input_started:
            self.sdl2.SDL_StopTextInput()
            self.text_input_started = False
        for attr in ["font_title", "font_ui", "font_small", "font_text", "font_key"]:
            font = getattr(self, attr)
            if font:
                self.sdlttf.TTF_CloseFont(font)
                setattr(self, attr, None)
        if self.renderer:
            self.sdl2.SDL_DestroyRenderer(self.renderer)
            self.renderer = None
        if self.window:
            self.sdl2.SDL_DestroyWindow(self.window)
            self.window = None
        if self.ttf_ready:
            self.sdlttf.TTF_Quit()
            self.ttf_ready = False
        if self.sdl_ready:
            self.sdl2.SDL_Quit()
            self.sdl_ready = False

    def measure(self, text: str, font) -> tuple[int, int]:
        if not text:
            return (0, 0)
        w = c_int()
        h = c_int()
        self.sdlttf.TTF_SizeUTF8(font, c_text(text), byref(w), byref(h))
        return (int(w.value), int(h.value))

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        font,
        color: tuple[int, int, int, int] = COLOR_TEXT,
        max_width: int | None = None,
    ) -> None:
        if not text:
            return
        if max_width is not None:
            text = self.ellipsize(text, font, max_width)
        surface = self.sdlttf.TTF_RenderUTF8_Blended(font, c_text(text), sdl_color(self.sdl2, color))
        if not surface:
            return
        texture = self.sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        if texture:
            rect = self.sdl2.SDL_Rect(x, y, surface.contents.w, surface.contents.h)
            self.sdl2.SDL_RenderCopy(self.renderer, texture, None, byref(rect))
            self.sdl2.SDL_DestroyTexture(texture)
        self.sdl2.SDL_FreeSurface(surface)

    def ellipsize(self, text: str, font, max_width: int) -> str:
        if self.measure(text, font)[0] <= max_width:
            return text
        suffix = "..."
        value = text
        while value and self.measure(value + suffix, font)[0] > max_width:
            value = value[:-1]
        return value + suffix if value else suffix

    def wrap_text(self, text: str, font, max_width: int) -> list[str]:
        words = text.replace("\n", " \n ").split(" ")
        lines: list[str] = []
        current = ""
        for word in words:
            if word == "\n":
                lines.append(current.rstrip())
                current = ""
                continue
            candidate = word if not current else current + " " + word
            if self.measure(candidate, font)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current.rstrip())
                current = ""
            while word and self.measure(word, font)[0] > max_width:
                chunk = ""
                for char in word:
                    candidate_chunk = chunk + char
                    if chunk and self.measure(candidate_chunk, font)[0] > max_width:
                        break
                    chunk = candidate_chunk
                lines.append(chunk)
                word = word[len(chunk) :]
            current = word
        if current or not lines:
            lines.append(current.rstrip())
        return [line if line else "" for line in lines]

    def fill_rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int, int]) -> None:
        self.sdl2.SDL_SetRenderDrawColor(self.renderer, *color)
        rect = self.sdl2.SDL_Rect(x, y, w, h)
        self.sdl2.SDL_RenderFillRect(self.renderer, byref(rect))

    def draw_rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int, int]) -> None:
        self.sdl2.SDL_SetRenderDrawColor(self.renderer, *color)
        rect = self.sdl2.SDL_Rect(x, y, w, h)
        self.sdl2.SDL_RenderDrawRect(self.renderer, byref(rect))

    def draw_panel(self, x: int, y: int, w: int, h: int, fill: tuple[int, int, int, int], border=COLOR_PANEL_3) -> None:
        self.fill_rect(x, y, w, h, fill)
        self.draw_rect(x, y, w, h, border)

    def preview_font(self, style: PreviewStyle):
        if style == PreviewStyle.H1:
            return self.font_title
        if style == PreviewStyle.H2:
            return self.font_ui
        if style == PreviewStyle.META:
            return self.font_small
        return self.font_text

    def preview_color(self, style: PreviewStyle) -> tuple[int, int, int, int]:
        from .constants import COLOR_ACCENT, COLOR_ACCENT_2, COLOR_MUTED, COLOR_TEXT, COLOR_WARN

        if style == PreviewStyle.H1:
            return COLOR_ACCENT_2
        if style == PreviewStyle.H2:
            return COLOR_ACCENT
        if style == PreviewStyle.QUOTE:
            return COLOR_WARN
        if style == PreviewStyle.META:
            return COLOR_MUTED
        return COLOR_TEXT

    def build_preview(self, markdown: str) -> list[PreviewLine]:
        items: list[PreviewLine] = []
        for block in parse_markdown_blocks(markdown):
            font = self.preview_font(block.style)
            wrap_width = LOGICAL_WIDTH - 52 - block.indent
            lines = self.wrap_text(plain_markdown_text(block.text), font, wrap_width)
            if not lines:
                lines = [""]
            for line in lines:
                items.append(
                    PreviewLine(
                        text=line,
                        style=block.style,
                        indent=block.indent,
                        height=max(18, self.measure(line or "M", font)[1] + 4),
                    )
                )
        return items or [PreviewLine("(empty)", PreviewStyle.META, 0, 18)]

    def visual_lines(self, text: str, cursor: int, max_cols: int) -> tuple[list[str], int, int]:
        return visual_lines(text, cursor, max_cols)

    def decode_text_input(self, event) -> str:
        raw = bytes(event.text.text)
        raw = raw.split(b"\x00", 1)[0]
        return raw.decode("utf-8", "ignore")
