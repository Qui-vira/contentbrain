#!/bin/bash
# Remote Terminal for Claude Code (Phone Access)
# Serves a web terminal on port 7681 with basic auth
# Access via Tailscale IP from your phone: http://100.x.x.x:7681

# ---- CONFIG ----
PORT=7681
USERNAME="quiv"
PASSWORD="contentbrain2026"
SHELL_PATH="bash"
WORKING_DIR="$HOME/onedrive/desktop/contentbrain"
# -----------------

echo "Starting ttyd web terminal on port $PORT..."
echo "Access: http://localhost:$PORT"
echo "Auth: $USERNAME / [hidden]"
echo ""
echo "To access from phone:"
echo "  1. Make sure Tailscale is running on both PC and phone"
echo "  2. Open http://[your-tailscale-ip]:$PORT in phone browser"
echo "  3. Run 'claude' to start Claude Code"
echo ""

cd "$WORKING_DIR" || exit 1

TTYD_PATH="$HOME/AppData/Local/Microsoft/WinGet/Packages/tsl0922.ttyd_Microsoft.Winget.Source_8wekyb3d8bbwe/ttyd.exe"

"$TTYD_PATH" \
  --port "$PORT" \
  --credential "$USERNAME:$PASSWORD" \
  --writable \
  "$SHELL_PATH"
