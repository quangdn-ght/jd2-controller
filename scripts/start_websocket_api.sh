#!/bin/bash
# Start JDownloader WebSocket API Server

cd "$(dirname "$0")/.."

echo "=================================="
echo "JDownloader WebSocket API Server"
echo "=================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "✗ Virtual environment not found!"
    echo "  Run: python3 -m venv venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠ Warning: .env file not found"
    echo "  Please configure your credentials first"
fi

# Check if JDownloader is running
if ! pgrep -f "JDownloader.jar" > /dev/null; then
    echo "⚠ Warning: JDownloader is not running"
    echo "  Starting JDownloader..."
    ./scripts/start_jd2.sh
    sleep 3
fi

echo ""
echo "🚀 Starting WebSocket API Server..."
echo "   🎨 Demo Client: http://localhost:8001/demo"
echo "   🌐 Web UI: http://localhost:8001/"
echo "   📡 WebSocket: ws://localhost:8001/ws"
echo "   📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 src/api/websocket_api.py
