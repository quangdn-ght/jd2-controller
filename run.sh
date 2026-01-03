#!/bin/bash
# Start JDownloader Controller in development or production mode

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Virtual environment not found at $SCRIPT_DIR/venv"
    echo "   Run: ./setup_venv.sh"
    exit 1
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run main.py with all arguments
exec "$VENV_PYTHON" main.py "$@"
