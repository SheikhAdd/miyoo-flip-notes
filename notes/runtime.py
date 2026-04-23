from __future__ import annotations

import sys
import traceback
from typing import Callable, Protocol

from .config_store import ConfigStore
from .controller import NotesController
from .crashlog import append_crash_log
from .paths import resolve_runtime_paths
from .render import NotesUi
from .storage import NoteRepository


class SupportsCleanup(Protocol):
    def cleanup(self) -> bool: ...


class SupportsRuntime(Protocol):
    controller: SupportsCleanup

    def run(self) -> int: ...


class NotesRuntime:
    def __init__(self) -> None:
        self.paths = resolve_runtime_paths()
        self.ui = NotesUi(runtime_paths=self.paths)
        self.controller = NotesController(
            ui=self.ui,
            sdl2_module=self.ui.sdl2,
            config_store=ConfigStore(runtime_paths=self.paths),
            repository=NoteRepository(runtime_paths=self.paths),
        )

    def run(self) -> int:
        self.ui.init_sdl()
        self.controller.state.char_width, self.controller.state.line_height = self.ui.refresh_text_font(
            self.controller.state.config.text_scale_percent
        )
        self.controller.notes.refresh_notes()
        running = True
        event = self.ui.sdl2.SDL_Event()

        while running:
            while self.ui.sdl2.SDL_PollEvent(event) != 0:
                if event.type == self.ui.sdl2.SDL_QUIT:
                    running = False
                elif event.type == self.ui.sdl2.SDL_KEYDOWN:
                    sym = int(event.key.keysym.sym)
                    running = self.controller.handle_key(sym)
                    self.controller.start_key_repeat(sym)
                elif event.type == self.ui.sdl2.SDL_KEYUP:
                    self.controller.stop_key_repeat(int(event.key.keysym.sym))
                elif event.type == self.ui.sdl2.SDL_TEXTINPUT:
                    self.controller.handle_text_input(self.ui.decode_text_input(event))

            self.controller.process_key_repeats()
            self.controller.notes.save_dirty_note(force=False)
            self.controller.editor.prepare_frame()
            self.ui.render(self.controller.state)
            self.ui.sdl2.SDL_Delay(16)
        return 0


def report_stack(stack_text: str, crash_logger: Callable[[str], None], stderr_writer: Callable[[str], None] | None) -> None:
    crash_logger(stack_text)
    if stderr_writer is not None:
        stderr_writer(stack_text)


def cleanup_runtime(runtime: SupportsRuntime | None, crash_logger: Callable[[str], None], stderr_writer: Callable[[str], None] | None) -> None:
    if runtime is None:
        return
    try:
        runtime.controller.cleanup()
    except Exception:
        report_stack(traceback.format_exc(), crash_logger, stderr_writer)


def main(
    runtime_factory: Callable[[], SupportsRuntime] = NotesRuntime,
    crash_logger: Callable[[str], None] = append_crash_log,
    stderr_writer: Callable[[str], None] | None = None,
) -> int:
    runtime: SupportsRuntime | None = None
    if stderr_writer is None:
        stderr_writer = sys.stderr.write
    try:
        runtime = runtime_factory()
        return runtime.run()
    except Exception:
        report_stack(traceback.format_exc(), crash_logger, stderr_writer)
        return 1
    finally:
        cleanup_runtime(runtime, crash_logger, stderr_writer)
