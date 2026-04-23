from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


APP_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RuntimePaths:
    app_root: Path
    device_sdcard_root: Path
    data_dir: Path
    config_path: Path
    log_path: Path
    crash_log_path: Path
    sdl_exlibs: Path
    sdl_dll_path: str
    font_ui: Path
    font_mono: Path

    def device_path(self, *parts: str) -> Path:
        return self.device_sdcard_root.joinpath(*parts)


def _env_path(environ: Mapping[str, str], name: str, default: Path) -> Path:
    return Path(environ.get(name, str(default)))


def resolve_runtime_paths(
    environ: Mapping[str, str] | None = None,
    app_root: Path | None = None,
) -> RuntimePaths:
    env = dict(os.environ if environ is None else environ)
    root = APP_ROOT if app_root is None else Path(app_root)
    device_sdcard_root = Path(env.get("MIYOO_SDCARD_ROOT", "/mnt/SDCARD"))

    default_data_dir = (
        device_sdcard_root / "Data" / "Notes"
        if device_sdcard_root.exists()
        else root / "data"
    )
    data_dir = _env_path(env, "NOTES_DIR", default_data_dir)

    return RuntimePaths(
        app_root=root,
        device_sdcard_root=device_sdcard_root,
        data_dir=data_dir,
        config_path=data_dir / "settings.json",
        log_path=data_dir / "notes.log",
        crash_log_path=data_dir / "notes-crash.log",
        sdl_exlibs=_env_path(
            env,
            "NOTES_SDL_EXLIBS",
            device_sdcard_root / "App" / "PortMaster" / "PortMaster" / "exlibs",
        ),
        sdl_dll_path=env.get(
            "NOTES_SDL_DLL_PATH",
            str(device_sdcard_root / "System" / "lib" / "SDL2"),
        ),
        font_ui=_env_path(
            env,
            "NOTES_FONT_UI",
            device_sdcard_root / "System" / "resources" / "DejaVuSans.ttf",
        ),
        font_mono=_env_path(
            env,
            "NOTES_FONT_MONO",
            device_sdcard_root / "App" / "PixelReader" / "resources" / "fonts" / "DejaVuSansMono.ttf",
        ),
    )
