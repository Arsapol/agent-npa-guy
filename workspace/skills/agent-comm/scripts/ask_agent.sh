#!/usr/bin/env bash
# ask_agent.sh — Send a message to another nanobot agent and return clean response
#
# Usage: bash ask_agent.sh "<message>" "<workspace>" "<config>" [timeout_s]
#
# Arguments:
#   $1  message          - The message to send to the target agent
#   $2  target_workspace - Absolute path to target agent's workspace directory
#   $3  target_config    - Absolute path to target agent's config.json
#   $4  timeout          - Optional timeout in seconds (default: 120)
#
# Output: Clean response text (nanobot banners and progress lines stripped)
# Exit codes: 0=success, 1=bad args, 2=missing files, 3=timeout, 4=nanobot error

set -euo pipefail

# --- Validate arguments ---
if [ $# -lt 3 ]; then
    echo "ERROR: Missing arguments"
    echo "Usage: bash ask_agent.sh \"<message>\" \"<workspace>\" \"<config>\" [timeout_s]"
    exit 1
fi

MESSAGE="$1"
TARGET_WORKSPACE="$2"
TARGET_CONFIG="$3"
TIMEOUT="${4:-120}"

# --- Validate paths ---
if [ ! -d "$TARGET_WORKSPACE" ]; then
    echo "ERROR: Target workspace not found: $TARGET_WORKSPACE"
    exit 2
fi

if [ ! -f "$TARGET_CONFIG" ]; then
    echo "ERROR: Target config not found: $TARGET_CONFIG"
    exit 2
fi

# --- Resolve timeout command (macOS uses gtimeout from coreutils) ---
TIMEOUT_CMD=""
if command -v timeout &>/dev/null; then
    TIMEOUT_CMD="timeout"
elif command -v gtimeout &>/dev/null; then
    TIMEOUT_CMD="gtimeout"
fi

# --- Execute ---
if [ -n "$TIMEOUT_CMD" ]; then
    RAW_OUTPUT=$($TIMEOUT_CMD "$TIMEOUT" nanobot agent \
        -m "$MESSAGE" \
        -w "$TARGET_WORKSPACE" \
        -c "$TARGET_CONFIG" \
        --no-markdown 2>&1) || {
        EXIT_CODE=$?
        if [ "$EXIT_CODE" -eq 124 ]; then
            echo "ERROR: Agent timed out after ${TIMEOUT}s"
            exit 3
        else
            echo "ERROR: nanobot agent failed (exit code: $EXIT_CODE)"
            echo "$RAW_OUTPUT"
            exit 4
        fi
    }
else
    # No timeout command available — run without timeout
    RAW_OUTPUT=$(nanobot agent \
        -m "$MESSAGE" \
        -w "$TARGET_WORKSPACE" \
        -c "$TARGET_CONFIG" \
        --no-markdown 2>&1) || {
        EXIT_CODE=$?
        echo "ERROR: nanobot agent failed (exit code: $EXIT_CODE)"
        echo "$RAW_OUTPUT"
        exit 4
    }
fi

# --- Clean output ---
# Strip nanobot banner lines (🐈 nanobot), "Using config:" line,
# template creation lines ("  Created ..."), and empty leading lines
CLEAN_OUTPUT=$(echo "$RAW_OUTPUT" \
    | grep -v '^Using config:' \
    | grep -v '^[[:space:]]*Created ' \
    | grep -v '^🐈' \
    | sed '/./,$!d')

echo "$CLEAN_OUTPUT"
