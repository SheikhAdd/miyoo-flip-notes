from __future__ import annotations

from .keyboard_geometry import remap_selection
from .layouts import LAYOUT_LIBRARY, LAYOUT_ORDER, alpha_layout_ids, get_layout, normalized_active_layouts
from .models import AppState, LayoutFamily
from .texts import ERROR_SYMBOLS_LAYOUT_DISABLED


class LayoutManager:
    def __init__(self, state: AppState, flash_status: Callable[[str], None]) -> None:
        self.state = state
        self.flash_status = flash_status

    def layout_order(self) -> list[str]:
        return list(LAYOUT_ORDER)

    def active_layout_ids(self) -> list[str]:
        self.state.config.active_layouts = normalized_active_layouts(self.state.config.active_layouts)
        return list(self.state.config.active_layouts)

    def ensure_valid_layout(self) -> None:
        active = self.active_layout_ids()
        if self.state.layout_id not in active:
            self.apply_layout(active[0])

    def apply_layout(self, layout_id: str) -> None:
        if layout_id not in LAYOUT_LIBRARY:
            return
        old_rows = get_layout(self.state.layout_id).rows if self.state.layout_id in LAYOUT_LIBRARY else get_layout(layout_id).rows
        new_rows = get_layout(layout_id).rows
        row, col = remap_selection(old_rows, new_rows, self.state.key_row, self.state.key_col)
        self.state.layout_id = layout_id
        self.state.key_row = row
        self.state.key_col = col

    def cycle_layout(self, direction: int) -> None:
        active = self.active_layout_ids()
        if len(active) <= 1:
            return
        current = self.state.layout_id if self.state.layout_id in active else active[0]
        index = active.index(current)
        self.apply_layout(active[(index + direction) % len(active)])

    def cycle_alpha_layout(self) -> None:
        active = alpha_layout_ids(self.active_layout_ids())
        if not active:
            return
        if self.state.layout_id not in active:
            self.apply_layout(active[0])
            return
        index = active.index(self.state.layout_id)
        self.apply_layout(active[(index + 1) % len(active)])

    def switch_to_symbols(self) -> None:
        active = self.active_layout_ids()
        if "symbols_basic" in active:
            self.state.previous_layout_id = self.state.layout_id
            self.apply_layout("symbols_basic")
        else:
            self.flash_status(ERROR_SYMBOLS_LAYOUT_DISABLED)

    def switch_to_alpha(self) -> None:
        active = self.active_layout_ids()
        for layout_id in active:
            if get_layout(layout_id).family == LayoutFamily.ALPHA:
                self.apply_layout(layout_id)
                return
        if active:
            self.apply_layout(active[0])

    def toggle_symbols_layout(self) -> None:
        if get_layout(self.state.layout_id).family == LayoutFamily.SYMBOLS:
            active = self.active_layout_ids()
            if self.state.previous_layout_id in active and self.state.previous_layout_id != "symbols_basic":
                self.apply_layout(self.state.previous_layout_id)
            else:
                self.switch_to_alpha()
        else:
            self.switch_to_symbols()
