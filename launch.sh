#!/bin/sh

APP_DIR=$(dirname "$0")
cd "$APP_DIR" || exit 1
APP_DIR=$(pwd)
NOTES_DIR="${NOTES_DIR:-/mnt/SDCARD/Data/Notes}"
export NOTES_DIR

mkdir -p "$NOTES_DIR"
exec > "$NOTES_DIR/notes-launch.log" 2>&1

echo "Starting Notes"
echo "APP_DIR=$APP_DIR"
echo "NOTES_DIR=$NOTES_DIR"

export PATH="/mnt/SDCARD/System/bin:/mnt/SDCARD/System/usr/miyoo/bin:/usr/miyoo/bin:/usr/bin:/bin:$PATH"
export LD_LIBRARY_PATH="/mnt/SDCARD/System/lib:/mnt/SDCARD/System/lib/SDL2:/usr/miyoo/lib:/usr/lib:$LD_LIBRARY_PATH"
export PYSDL2_DLL_PATH="${PYSDL2_DLL_PATH:-/mnt/SDCARD/System/lib/SDL2}"

GPTOKEYB_PID=""
cleanup_gptokeyb() {
    if [ -n "$GPTOKEYB_PID" ]; then
        kill "$GPTOKEYB_PID" 2>/dev/null
    fi
}
trap cleanup_gptokeyb EXIT INT TERM

if [ -x "$APP_DIR/gptokeyb" ]; then
    if [ ! -f "$APP_DIR/gamecontrollerdb.txt" ]; then
        echo "WARN: gamecontrollerdb.txt is missing; gptokeyb will use its defaults"
    fi
    SDL_GAMECONTROLLERCONFIG_FILE="$APP_DIR/gamecontrollerdb.txt" "$APP_DIR/gptokeyb" -k "notes" -c "$APP_DIR/notes.gptk" &
    GPTOKEYB_PID="$!"
    sleep 1
else
    echo "WARN: gptokeyb is missing; built-in gamepad mapping will not be available"
fi

PYTHON_BIN="/mnt/SDCARD/System/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" "$APP_DIR/notes_app.py"
STATUS="$?"

if [ "$STATUS" -ne 0 ]; then
    INFO_SCREEN="/mnt/SDCARD/System/usr/miyoo/scripts/infoscreen.sh"
    if [ -x "$INFO_SCREEN" ]; then
        "$INFO_SCREEN" -m "Notes crashed. Check Data/Notes/notes-crash.log" -t 3 >/dev/null 2>&1
    fi
fi

echo "Notes exited with status $STATUS"
exit "$STATUS"
