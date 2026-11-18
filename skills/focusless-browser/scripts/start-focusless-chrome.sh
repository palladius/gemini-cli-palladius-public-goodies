#!/usr/bin/env bash
# Level-2 (Xephyr) & Level-3 (Xvfb) Focusless Chrome Launcher (Linux Only)
#
# Launches a real desktop Chrome (NO --enable-automation!) inside an isolated X11 display
# so CDP / browser automation can NEVER steal host keyboard focus, raise host windows, or
# overwrite the host clipboard.
#
# Platform Support:
#   - Linux: Supported (requires Xephyr or Xvfb + google-chrome/chromium).
#   - macOS: Untested / Unsupported (?) — Xephyr is not natively available on macOS.
#
# Usage:
#   start-focusless-chrome.sh [--mode xephyr|xvfb] [--display :99] [--port 9222] [--profile-dir PATH]
#   start-focusless-chrome.sh --stop [--display :99] [--port 9222]

set -euo pipefail

MODE="xephyr"
DISP=":99"
PORT="9222"
SCREEN="1366x900"
PROFILE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/chrome-focusless-agent"
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/focusless-browser"
ACTION="start"
START_URL="about:blank"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:?}"; shift 2 ;;
    --display) DISP="${2:?}"; shift 2 ;;
    --port) PORT="${2:?}"; shift 2 ;;
    --screen) SCREEN="${2:?}"; shift 2 ;;
    --profile-dir) PROFILE_DIR="${2:?}"; shift 2 ;;
    --url) START_URL="${2:?}"; shift 2 ;;
    --stop) ACTION="stop"; shift ;;
    -h|--help)
      sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

OS_NAME="$(uname -s)"
if [[ "$OS_NAME" != "Linux" ]]; then
  echo "❌ start-focusless-chrome.sh (Level 2 Xephyr / Level 3 Xvfb) requires Linux (detected: $OS_NAME)." >&2
  echo "   On macOS (?), use Level 1 focusless CDP (Emulation.setFocusEmulationEnabled + focusless_notify.py)." >&2
  exit 1
fi

mkdir -p "$PROFILE_DIR" "$LOG_DIR"
SAFE_DISP="${DISP//:/}"
DISPLAY_PID_FILE="$LOG_DIR/display_${SAFE_DISP}.pid"
CHROME_PID_FILE="$LOG_DIR/chrome_${PORT}.pid"

stop_pid_file() {
  local pf="$1"
  if [[ -f "$pf" ]]; then
    local pid
    pid="$(cat "$pf" || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 0.5
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pf"
  fi
}

if [[ "$ACTION" == "stop" ]]; then
  stop_pid_file "$CHROME_PID_FILE"
  stop_pid_file "$DISPLAY_PID_FILE"
  echo "🛑 Stopped focusless Chrome (port $PORT) and display ($DISP). Profile preserved in $PROFILE_DIR"
  exit 0
fi

# Find Chrome/Chromium binary
CHROME_BIN=""
for cand in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$cand" >/dev/null 2>&1; then
    CHROME_BIN="$(command -v "$cand")"
    break
  fi
done
if [[ -z "$CHROME_BIN" ]]; then
  echo "❌ No google-chrome or chromium binary found in PATH." >&2
  exit 1
fi

# Start isolated X display server if not already running on $DISP
if [[ ! -S "/tmp/.X11-unix/X${SAFE_DISP}" ]]; then
  case "$MODE" in
    xephyr)
      if ! command -v Xephyr >/dev/null 2>&1; then
        echo "❌ Xephyr not found. Install it (e.g. sudo apt install xserver-xephyr) or pass --mode xvfb." >&2
        exit 1
      fi
      nohup Xephyr "$DISP" -screen "$SCREEN" -ac -br -noreset -no-host-grab \
        -title "🤖 Focusless Agent Chrome ($DISP)" \
        >"$LOG_DIR/xephyr_${SAFE_DISP}.log" 2>&1 &
      echo $! > "$DISPLAY_PID_FILE"
      ;;
    xvfb)
      if ! command -v Xvfb >/dev/null 2>&1; then
        echo "❌ Xvfb not found. Install it (e.g. sudo apt install xvfb)." >&2
        exit 1
      fi
      nohup Xvfb "$DISP" -screen 0 "${SCREEN}x24" -ac -nolisten tcp \
        >"$LOG_DIR/xvfb_${SAFE_DISP}.log" 2>&1 &
      echo $! > "$DISPLAY_PID_FILE"
      ;;
    *)
      echo "❌ Unsupported --mode '$MODE'. Use 'xephyr' or 'xvfb'." >&2
      exit 2
      ;;
  esac
  sleep 1.2
fi

# Launch real desktop Chrome (NO --enable-automation!) inside the isolated X display
DISPLAY="$DISP" nohup "$CHROME_BIN" \
  --user-data-dir="$PROFILE_DIR" \
  --remote-debugging-port="$PORT" \
  --no-first-run \
  --no-default-browser-check \
  "$START_URL" \
  >"$LOG_DIR/chrome_${PORT}.log" 2>&1 &
echo $! > "$CHROME_PID_FILE"
sleep 1.5

echo "✅ Focusless Chrome running on DISPLAY=$DISP ($MODE), CDP port=$PORT"
echo "   Profile : $PROFILE_DIR"
echo "   Logs    : $LOG_DIR/chrome_${PORT}.log"
echo "   Inspect : curl -s http://127.0.0.1:${PORT}/json/version"
