from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .constants import LOGICAL_HEIGHT, LOGICAL_WIDTH


@dataclass(frozen=True)
class WindowConfig:
    mode: str
    width: int
    height: int

    @property
    def fullscreen(self) -> bool:
        return self.mode == "fullscreen"


def parse_window_scale(value: str | None, default: int = 2) -> int:
    if value is None:
        return default
    try:
        scale = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(6, scale))


def resolve_window_config(environ: Mapping[str, str]) -> WindowConfig:
    mode = environ.get("NOTES_WINDOW_MODE", "fullscreen").strip().lower()
    if mode == "windowed":
        scale = parse_window_scale(environ.get("NOTES_WINDOW_SCALE"))
        return WindowConfig(
            mode="windowed",
            width=LOGICAL_WIDTH * scale,
            height=LOGICAL_HEIGHT * scale,
        )
    return WindowConfig(
        mode="fullscreen",
        width=LOGICAL_WIDTH,
        height=LOGICAL_HEIGHT,
    )
