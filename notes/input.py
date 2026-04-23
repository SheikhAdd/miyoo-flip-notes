from __future__ import annotations

from enum import Enum

from .models import AppConfig, ButtonScheme


class Action(str, Enum):
    CANCEL = "cancel"
    MENU = "menu"
    CONFIRM = "confirm"
    ENTER = "enter"
    DELETE = "delete"
    SPACE = "space"
    TOGGLE_SHIFT = "toggle_shift"
    TOGGLE_SYMBOLS = "toggle_symbols"
    PREV_LAYOUT = "prev_layout"
    NEXT_LAYOUT = "next_layout"
    NAV_UP = "nav_up"
    NAV_DOWN = "nav_down"
    NAV_LEFT = "nav_left"
    NAV_RIGHT = "nav_right"
    CURSOR_LEFT = "cursor_left"
    CURSOR_RIGHT = "cursor_right"
    CURSOR_LINE_UP = "cursor_line_up"
    CURSOR_LINE_DOWN = "cursor_line_down"


def resolve_action(sdl2, config: AppConfig, sym: int) -> Action | None:
    confirm_key = sdl2.SDLK_LCTRL if config.button_scheme == ButtonScheme.STANDARD else sdl2.SDLK_LALT
    shift_key = sdl2.SDLK_LALT if config.button_scheme == ButtonScheme.STANDARD else sdl2.SDLK_LCTRL

    mapping = {
        sdl2.SDLK_ESCAPE: Action.CANCEL,
        sdl2.SDLK_RCTRL: Action.MENU,
        confirm_key: Action.CONFIRM,
        sdl2.SDLK_RETURN: Action.ENTER,
        sdl2.SDLK_KP_ENTER: Action.ENTER,
        sdl2.SDLK_BACKSPACE: Action.DELETE,
        sdl2.SDLK_TAB: Action.SPACE,
        shift_key: Action.TOGGLE_SHIFT,
        sdl2.SDLK_F1: Action.TOGGLE_SYMBOLS,
        sdl2.SDLK_HOME: Action.PREV_LAYOUT,
        sdl2.SDLK_END: Action.NEXT_LAYOUT,
        sdl2.SDLK_UP: Action.NAV_UP,
        sdl2.SDLK_DOWN: Action.NAV_DOWN,
        sdl2.SDLK_LEFT: Action.NAV_LEFT,
        sdl2.SDLK_RIGHT: Action.NAV_RIGHT,
        sdl2.SDLK_INSERT: Action.CURSOR_LEFT,
        sdl2.SDLK_DELETE: Action.CURSOR_RIGHT,
        sdl2.SDLK_PAGEUP: Action.CURSOR_LINE_UP,
        sdl2.SDLK_PAGEDOWN: Action.CURSOR_LINE_DOWN,
    }
    return mapping.get(sym)


REPEATABLE_ACTIONS = {
    Action.DELETE,
    Action.SPACE,
    Action.NAV_UP,
    Action.NAV_DOWN,
    Action.NAV_LEFT,
    Action.NAV_RIGHT,
    Action.CURSOR_LEFT,
    Action.CURSOR_RIGHT,
    Action.CURSOR_LINE_UP,
    Action.CURSOR_LINE_DOWN,
}

