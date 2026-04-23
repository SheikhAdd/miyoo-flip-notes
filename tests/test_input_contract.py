from __future__ import annotations

import unittest
from pathlib import Path

from notes.input import Action, resolve_action
from notes.models import AppConfig, AppMode, AppState, ButtonScheme
from notes.texts import footer_text


class FakeSdl:
    SDLK_ESCAPE = 1
    SDLK_RCTRL = 2
    SDLK_LCTRL = 3
    SDLK_LALT = 4
    SDLK_RETURN = 5
    SDLK_KP_ENTER = 6
    SDLK_BACKSPACE = 7
    SDLK_TAB = 8
    SDLK_F1 = 9
    SDLK_HOME = 10
    SDLK_END = 11
    SDLK_UP = 12
    SDLK_DOWN = 13
    SDLK_LEFT = 14
    SDLK_RIGHT = 15
    SDLK_INSERT = 16
    SDLK_DELETE = 17
    SDLK_PAGEUP = 18
    SDLK_PAGEDOWN = 19


KEY_NAME_TO_SYM = {
    "esc": FakeSdl.SDLK_ESCAPE,
    "rightctrl": FakeSdl.SDLK_RCTRL,
    "leftctrl": FakeSdl.SDLK_LCTRL,
    "leftalt": FakeSdl.SDLK_LALT,
    "enter": FakeSdl.SDLK_RETURN,
    "backspace": FakeSdl.SDLK_BACKSPACE,
    "tab": FakeSdl.SDLK_TAB,
    "f1": FakeSdl.SDLK_F1,
    "home": FakeSdl.SDLK_HOME,
    "end": FakeSdl.SDLK_END,
    "up": FakeSdl.SDLK_UP,
    "down": FakeSdl.SDLK_DOWN,
    "left": FakeSdl.SDLK_LEFT,
    "right": FakeSdl.SDLK_RIGHT,
    "insert": FakeSdl.SDLK_INSERT,
    "delete": FakeSdl.SDLK_DELETE,
    "pageup": FakeSdl.SDLK_PAGEUP,
    "pagedown": FakeSdl.SDLK_PAGEDOWN,
}


def load_gptk_mapping() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    mapping: dict[str, str] = {}
    for raw_line in (root / "notes.gptk").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        mapping[key] = value
    return mapping


class InputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gptk = load_gptk_mapping()

    def action_for_gptk(self, control_name: str, config: AppConfig) -> Action | None:
        key_name = self.gptk[control_name]
        return resolve_action(FakeSdl, config, KEY_NAME_TO_SYM[key_name])

    def test_standard_scheme_matches_gptokeyb_contract(self) -> None:
        config = AppConfig(button_scheme=ButtonScheme.STANDARD)

        self.assertEqual(self.action_for_gptk("back", config), Action.CANCEL)
        self.assertEqual(self.action_for_gptk("guide", config), Action.CANCEL)
        self.assertEqual(self.action_for_gptk("start", config), Action.MENU)
        self.assertEqual(self.action_for_gptk("a", config), Action.CONFIRM)
        self.assertEqual(self.action_for_gptk("b", config), Action.TOGGLE_SHIFT)
        self.assertEqual(self.action_for_gptk("x", config), Action.DELETE)
        self.assertEqual(self.action_for_gptk("y", config), Action.SPACE)
        self.assertEqual(self.action_for_gptk("l1", config), Action.PREV_LAYOUT)
        self.assertEqual(self.action_for_gptk("r1", config), Action.NEXT_LAYOUT)
        self.assertEqual(self.action_for_gptk("l2", config), Action.TOGGLE_SYMBOLS)
        self.assertEqual(self.action_for_gptk("r2", config), Action.ENTER)
        self.assertEqual(self.action_for_gptk("up", config), Action.NAV_UP)
        self.assertEqual(self.action_for_gptk("down", config), Action.NAV_DOWN)
        self.assertEqual(self.action_for_gptk("left", config), Action.NAV_LEFT)
        self.assertEqual(self.action_for_gptk("right", config), Action.NAV_RIGHT)
        self.assertEqual(self.action_for_gptk("left_analog_up", config), Action.NAV_UP)
        self.assertEqual(self.action_for_gptk("left_analog_down", config), Action.NAV_DOWN)
        self.assertEqual(self.action_for_gptk("left_analog_left", config), Action.NAV_LEFT)
        self.assertEqual(self.action_for_gptk("left_analog_right", config), Action.NAV_RIGHT)
        self.assertEqual(self.action_for_gptk("right_analog_up", config), Action.CURSOR_LINE_UP)
        self.assertEqual(self.action_for_gptk("right_analog_down", config), Action.CURSOR_LINE_DOWN)
        self.assertEqual(self.action_for_gptk("right_analog_left", config), Action.CURSOR_LEFT)
        self.assertEqual(self.action_for_gptk("right_analog_right", config), Action.CURSOR_RIGHT)

    def test_swapped_scheme_flips_confirm_and_shift_only(self) -> None:
        config = AppConfig(button_scheme=ButtonScheme.SWAPPED)

        self.assertEqual(self.action_for_gptk("a", config), Action.TOGGLE_SHIFT)
        self.assertEqual(self.action_for_gptk("b", config), Action.CONFIRM)
        self.assertEqual(self.action_for_gptk("x", config), Action.DELETE)
        self.assertEqual(self.action_for_gptk("y", config), Action.SPACE)

    def test_footer_labels_follow_selected_button_scheme(self) -> None:
        standard_state = AppState(config=AppConfig(button_scheme=ButtonScheme.STANDARD))
        swapped_state = AppState(config=AppConfig(button_scheme=ButtonScheme.SWAPPED))
        standard_edit_state = AppState(mode=AppMode.EDIT, config=AppConfig(button_scheme=ButtonScheme.STANDARD))
        swapped_edit_state = AppState(mode=AppMode.EDIT, config=AppConfig(button_scheme=ButtonScheme.SWAPPED))

        self.assertIn("B Open", footer_text(standard_state))
        self.assertIn("A Open", footer_text(swapped_state))
        self.assertIn("A Shift", footer_text(standard_edit_state))
        self.assertIn("B Shift", footer_text(swapped_edit_state))


if __name__ == "__main__":
    unittest.main()
