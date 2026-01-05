#!/bin/bash
# Start JDownloader Controller in development or production mode

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Virtual environment not found at $PROJECT_DIR/venv"
    echo "   Run: ./setup_venv.sh"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR"

# Run main.py with all arguments
exec "$VENV_PYTHON" main.py "$@"
