from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from notes.config_store import ConfigStore, parse_bool, parse_button_scheme
from notes.models import AppConfig, ButtonScheme


class ConfigStoreTests(unittest.TestCase):
    def test_normalize_clamps_and_fixes_layouts(self) -> None:
        store = ConfigStore()
        config = AppConfig(
            button_scheme=ButtonScheme.STANDARD,
            active_layouts=["missing"],
            autosave_enabled=True,
            autosave_minutes=999,
            text_scale_percent=111,
        )
        normalized = store.normalize(config)
        self.assertEqual(normalized.active_layouts, ["en_qwerty", "ru_jcuken", "kz_cyrillic", "symbols_basic"])
        self.assertEqual(normalized.autosave_minutes, 120)
        self.assertEqual(normalized.text_scale_percent, 115)

    def test_parse_bool_accepts_string_false(self) -> None:
        self.assertFalse(parse_bool("false", True))
        self.assertTrue(parse_bool("yes", False))

    def test_invalid_json_is_backed_up_and_defaults_are_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir)
            config_path = data_dir / "settings.json"
            config_path.write_text("{invalid json", encoding="utf-8")
            warnings: list[tuple[str, str]] = []
            store = ConfigStore(config_path=config_path, data_dir=data_dir, warning_logger=lambda title, body: warnings.append((title, body)))

            loaded = store.load()

            self.assertEqual(loaded.active_layouts, ["en_qwerty", "ru_jcuken", "kz_cyrillic", "symbols_basic"])
            self.assertTrue(warnings)
            backups = list(data_dir.glob("settings.invalid-*.json"))
            self.assertEqual(len(backups), 1)

    def test_swap_ab_legacy_value_is_still_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir)
            config_path = data_dir / "settings.json"
            config_path.write_text('{"button_scheme":"swap_ab"}', encoding="utf-8")
            store = ConfigStore(config_path=config_path, data_dir=data_dir)

            loaded = store.load()

            self.assertEqual(loaded.button_scheme, ButtonScheme.SWAPPED)

    def test_unknown_button_scheme_falls_back_to_default(self) -> None:
        self.assertEqual(parse_button_scheme("legacy_alias", ButtonScheme.SWAPPED), ButtonScheme.SWAPPED)
        self.assertEqual(parse_button_scheme("unknown", ButtonScheme.STANDARD), ButtonScheme.STANDARD)


if __name__ == "__main__":
    unittest.main()
