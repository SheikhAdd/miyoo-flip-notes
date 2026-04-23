from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .constants import AUTOSAVE_MINUTES_OPTIONS, TEXT_SCALE_OPTIONS
from .crashlog import append_runtime_log
from .layouts import DEFAULT_LAYOUT_IDS, normalized_active_layouts
from .models import AppConfig, ButtonScheme
from .paths import RuntimePaths, resolve_runtime_paths
from .utils import clamp


BUTTON_SCHEME_NAMES = {
    ButtonScheme.STANDARD: "Standard: B select, A shift",
    ButtonScheme.SWAPPED: "Swapped: A select, B shift",
}

TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
LEGACY_BUTTON_SCHEME_ALIASES = {"swap_ab": ButtonScheme.SWAPPED}


def parse_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in TRUE_VALUES:
            return True
        if normalized in FALSE_VALUES:
            return False
    return default


def parse_int(value, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        normalized = value.strip()
        if normalized:
            return int(normalized)
    return default


def parse_button_scheme(value, default: ButtonScheme) -> ButtonScheme:
    if isinstance(value, ButtonScheme):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == ButtonScheme.STANDARD.value:
            return ButtonScheme.STANDARD
        if normalized == ButtonScheme.SWAPPED.value:
            return ButtonScheme.SWAPPED
        if normalized in LEGACY_BUTTON_SCHEME_ALIASES:
            return LEGACY_BUTTON_SCHEME_ALIASES[normalized]
    return default


class ConfigStore:
    def __init__(
        self,
        config_path: Path | None = None,
        data_dir: Path | None = None,
        warning_logger: Callable[[str, str], None] = append_runtime_log,
        runtime_paths: RuntimePaths | None = None,
    ) -> None:
        self.runtime_paths = runtime_paths or resolve_runtime_paths()
        self.config_path = config_path or self.runtime_paths.config_path
        self.data_dir = data_dir or self.config_path.parent
        self.warning_logger = warning_logger

    def backup_invalid_config(self, raw_text: str, reason: str) -> None:
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_path = self.config_path.with_name(f"{self.config_path.stem}.invalid-{timestamp}{self.config_path.suffix}")
            backup_path.write_text(raw_text, encoding="utf-8")
            self.warning_logger(
                "Config fallback to defaults",
                f"Config path: {self.config_path}\nReason: {reason}\nBackup: {backup_path}",
            )
        except OSError as exc:
            self.warning_logger(
                "Config fallback to defaults",
                f"Config path: {self.config_path}\nReason: {reason}\nBackup write failed: {exc}",
            )

    def load(self) -> AppConfig:
        config = AppConfig(active_layouts=list(DEFAULT_LAYOUT_IDS))
        if self.config_path.exists():
            try:
                raw_text = self.config_path.read_text(encoding="utf-8")
                loaded = json.loads(raw_text)
                if not isinstance(loaded, dict):
                    self.backup_invalid_config(raw_text, "Top-level JSON value is not an object")
                    return self.normalize(config)

                raw_layouts = loaded.get("active_layouts", config.active_layouts)
                active_layouts = list(raw_layouts) if isinstance(raw_layouts, list) else list(config.active_layouts)

                config = self.normalize(
                    AppConfig(
                        button_scheme=parse_button_scheme(loaded.get("button_scheme", config.button_scheme.value), config.button_scheme),
                        active_layouts=active_layouts,
                        autosave_enabled=parse_bool(loaded.get("autosave_enabled", config.autosave_enabled), config.autosave_enabled),
                        autosave_minutes=parse_int(loaded.get("autosave_minutes", config.autosave_minutes), config.autosave_minutes),
                        text_scale_percent=parse_int(
                            loaded.get("text_scale_percent", config.text_scale_percent),
                            config.text_scale_percent,
                        ),
                    )
                )
                return config
            except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
                raw_text = ""
                try:
                    raw_text = self.config_path.read_text(encoding="utf-8")
                except OSError:
                    raw_text = ""
                self.backup_invalid_config(raw_text, str(exc))
        return self.normalize(config)

    def normalize(self, config: AppConfig) -> AppConfig:
        button_scheme = parse_button_scheme(config.button_scheme, ButtonScheme.STANDARD)
        autosave_minutes = clamp(int(config.autosave_minutes or 5), 1, 120)
        text_scale_percent = int(config.text_scale_percent or 100)
        if text_scale_percent not in TEXT_SCALE_OPTIONS:
            text_scale_percent = min(TEXT_SCALE_OPTIONS, key=lambda value: abs(value - text_scale_percent))

        return AppConfig(
            button_scheme=button_scheme,
            active_layouts=normalized_active_layouts(config.active_layouts),
            autosave_enabled=bool(config.autosave_enabled),
            autosave_minutes=autosave_minutes,
            text_scale_percent=text_scale_percent,
        )

    def save(self, config: AppConfig) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        normalized = self.normalize(config)
        self.config_path.write_text(
            json.dumps(
                {
                    "button_scheme": normalized.button_scheme.value,
                    "active_layouts": normalized.active_layouts,
                    "autosave_enabled": normalized.autosave_enabled,
                    "autosave_minutes": normalized.autosave_minutes,
                    "text_scale_percent": normalized.text_scale_percent,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    @property
    def autosave_options(self) -> list[int]:
        return list(AUTOSAVE_MINUTES_OPTIONS)

    @property
    def text_scale_options(self) -> list[int]:
        return list(TEXT_SCALE_OPTIONS)
