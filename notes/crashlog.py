from __future__ import annotations

import sys
import time
from pathlib import Path

from .paths import RuntimePaths, resolve_runtime_paths


def append_runtime_log(
    title: str,
    body: str,
    path: Path | None = None,
    runtime_paths: RuntimePaths | None = None,
) -> None:
    message = ""
    resolved_paths = runtime_paths or resolve_runtime_paths()
    target_path = path or resolved_paths.log_path
    data_dir = target_path.parent if path is not None else resolved_paths.data_dir
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {title}\n{body}\n\n"
        with target_path.open("a", encoding="utf-8") as handle:
            handle.write(message)
    except OSError as exc:
        fallback = message or f"{title}\n{body}\n\n"
        try:
            sys.stderr.write(f"[notes-log-fallback] {exc}\n{fallback}")
        except OSError:
            return


def append_crash_log(stack_text: str, runtime_paths: RuntimePaths | None = None) -> None:
    resolved_paths = runtime_paths or resolve_runtime_paths()
    append_runtime_log("Crash", stack_text, path=resolved_paths.crash_log_path, runtime_paths=resolved_paths)
