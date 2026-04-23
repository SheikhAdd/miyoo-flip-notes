from __future__ import annotations

from typing import Callable, Protocol

from .config_store import ConfigStore
from .constants import LAYOUTS_VISIBLE_ROWS
from .layout_manager import LayoutManager
from .layouts import LAYOUT_LIBRARY
from .models import AppState, ButtonScheme
from .texts import STATUS_BUTTON_SCHEME_SAVED, autosave_interval_status, autosave_status, settings_save_error, text_scale_status


class SupportsSettingsUi(Protocol):
    def refresh_text_font(self, text_scale_percent: int) -> tuple[int, int]: ...


class SettingsManager:
    def __init__(
        self,
        state: AppState,
        config_store: ConfigStore,
        layouts: LayoutManager,
        ui: SupportsSettingsUi,
        flash_status: Callable[[str], None],
    ) -> None:
        self.state = state
        self.config_store = config_store
        self.layouts = layouts
        self.ui = ui
        self.flash_status = flash_status

    def persist_config(self) -> None:
        try:
            self.config_store.save(self.state.config)
        except OSError as exc:
            self.flash_status(settings_save_error(exc))

    def toggle_button_scheme(self) -> None:
        if self.state.config.button_scheme == ButtonScheme.STANDARD:
            self.state.config.button_scheme = ButtonScheme.SWAPPED
        else:
            self.state.config.button_scheme = ButtonScheme.STANDARD
        self.persist_config()
        self.flash_status(STATUS_BUTTON_SCHEME_SAVED)

    def toggle_autosave(self) -> None:
        self.state.config.autosave_enabled = not self.state.config.autosave_enabled
        self.persist_config()
        self.flash_status(autosave_status(self.state.config.autosave_enabled))

    def cycle_autosave_minutes(self) -> None:
        current = int(self.state.config.autosave_minutes)
        options = self.config_store.autosave_options
        if current not in options:
            current = 5
        index = options.index(current)
        self.state.config.autosave_minutes = options[(index + 1) % len(options)]
        self.persist_config()
        self.flash_status(autosave_interval_status(self.state.config.autosave_minutes))

    def cycle_text_scale(self) -> None:
        current = int(self.state.config.text_scale_percent)
        options = self.config_store.text_scale_options
        if current not in options:
            current = 100
        index = options.index(current)
        self.state.config.text_scale_percent = options[(index + 1) % len(options)]
        self.persist_config()
        self.state.char_width, self.state.line_height = self.ui.refresh_text_font(self.state.config.text_scale_percent)
        self.flash_status(text_scale_status(self.state.config.text_scale_percent))

    def toggle_layout_enabled(self, layout_id: str) -> None:
        active = self.layouts.active_layout_ids()
        if layout_id in active:
            if len(active) == 1:
                self.flash_status("At least one layout must stay enabled")
                return
            active = [item for item in active if item != layout_id]
        else:
            active.append(layout_id)
            active = sorted(active, key=lambda item: self.layouts.layout_order().index(item))

        self.state.config.active_layouts = active
        self.persist_config()
        self.layouts.ensure_valid_layout()
        self.flash_status("Layouts updated")

    def ensure_layout_visible(self) -> None:
        if self.state.layouts_index < self.state.layouts_scroll:
            self.state.layouts_scroll = self.state.layouts_index
        elif self.state.layouts_index >= self.state.layouts_scroll + LAYOUTS_VISIBLE_ROWS:
            self.state.layouts_scroll = self.state.layouts_index - LAYOUTS_VISIBLE_ROWS + 1
        self.state.layouts_scroll = max(0, min(self.state.layouts_scroll, max(0, len(LAYOUT_LIBRARY) - LAYOUTS_VISIBLE_ROWS)))
