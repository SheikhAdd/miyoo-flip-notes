# Architecture

The code is split into a few focused layers.

Runtime and wiring:

- `notes_app.py`: process entry point
- `notes/runtime.py`: bootstraps controller, UI, and the main event loop
- `notes/paths.py`: runtime path resolution and environment overrides
- `notes/crashlog.py`: crash logging helpers

Controller and state:

- `notes/controller.py`: top-level app coordination
- `notes/note_manager.py`: note lifecycle, selection, rename, delete, save-facing state
- `notes/editor_controller.py`: editor cursor movement, text editing state, and preview flow
- `notes/settings_manager.py`: settings state and persistence coordination
- `notes/layout_manager.py`: keyboard layout switching and active layout state
- `notes/controller_input.py`: input routing by mode
- `notes/controller_repeat.py`: held-key repeat rules and repeat execution
- `notes/controller_actions.py`: menus, overlays, and action dispatch helpers

Rendering:

- `notes/render.py`: SDL setup, font loading, and low-level drawing primitives
- `notes/render_layout.py`: shared geometry and layout calculations
- `notes/render_views.py`: main screen rendering
- `notes/render_overlays.py`: overlays, dialogs, and keyboard rendering
- `notes/desktop_window.py`: desktop preview window sizing and scaling rules

Persistence and data helpers:

- `notes/storage.py`: note file operations
- `notes/config_store.py`: settings load/save
- `notes/models.py`: typed app models
- `notes/texts.py`: UI strings

Pure logic and utilities:

- `notes/input.py`: key-to-action mapping
- `notes/editor_ops.py`: text editing helpers
- `notes/markdown_preview.py`: simplified markdown preview parsing
- `notes/viewports.py`: scroll and viewport helpers
- `notes/keyboard_geometry.py`: keyboard navigation helpers
- `notes/layouts.py`: built-in keyboard layouts
- `notes/constants.py`: shared dimensions and colors
- `notes/utils.py`: small shared helpers

This is a device-specific app, not a generic framework.
