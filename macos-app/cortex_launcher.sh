#!/bin/bash
# Cortex macOS App Launch Script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python executable
PYTHON_BIN="$SCRIPT_DIR/Python"

# Change to app directory
cd "$SCRIPT_DIR"

# Start the Flask server in background if not running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Starting Cortex server..."
    "$PYTHON_BIN" run.py > /tmp/cortex-server.log 2>&1 &
    sleep 2
fi

# Launch the GUI
exec "$PYTHON_BIN" cortex_gui.py
