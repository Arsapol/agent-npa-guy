#!/usr/bin/env bash
# Start/stop OSRM routing server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
OSRM_FILE="$DATA_DIR/thailand-latest.osrm"
PID_FILE="$DATA_DIR/osrm.pid"
PORT="${OSRM_PORT:-5001}"

case "${1:-start}" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "OSRM already running (PID $(cat "$PID_FILE")) on port $PORT"
            exit 0
        fi

        if [ ! -f "$OSRM_FILE.ebg" ]; then
            echo "ERROR: OSRM data not found at $OSRM_FILE.*. Run osrm_setup.sh first."
            exit 1
        fi

        echo "Starting OSRM on port $PORT..."
        osrm-routed --algorithm=MLD --port="$PORT" "$OSRM_FILE" &
        echo $! > "$PID_FILE"
        sleep 2

        if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "OSRM running (PID $(cat "$PID_FILE")) on http://localhost:$PORT"
        else
            echo "ERROR: OSRM failed to start"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;

    stop)
        if [ -f "$PID_FILE" ]; then
            kill "$(cat "$PID_FILE")" 2>/dev/null || true
            rm -f "$PID_FILE"
            echo "OSRM stopped"
        else
            echo "OSRM not running"
        fi
        ;;

    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "OSRM running (PID $(cat "$PID_FILE")) on port $PORT"
        else
            echo "OSRM not running"
            rm -f "$PID_FILE" 2>/dev/null
        fi
        ;;

    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
