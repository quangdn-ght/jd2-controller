#!/bin/bash
# Start JDownloader in headless mode and connect to cloud

echo "🔧 Starting JDownloader Cloud Connection..."

# Kill any existing JDownloader instances
sudo pkill -9 -f JDownloader.jar 2>/dev/null
sleep 2

# Check if JDownloader.jar exists
if [ ! -f "/opt/jd2/JDownloader.jar" ]; then
    echo "❌ Error: JDownloader.jar not found at /opt/jd2/"
    exit 1
fi

# Start JDownloader
echo "🚀 Starting JDownloader..."
cd /opt/jd2
sudo java -jar JDownloader.jar -norestart > /tmp/jd2.log 2>&1 &

# Wait for JDownloader to start
echo "⏳ Waiting for JDownloader to start (30 seconds)..."
sleep 30

# Check if running
if pgrep -f "JDownloader.jar" > /dev/null; then
    PID=$(pgrep -f "JDownloader.jar")
    echo "✅ JDownloader started successfully (PID: $PID)"
    echo "📝 Logs: tail -f /tmp/jd2.log"
    
    # Wait additional time for cloud connection
    echo "⏳ Waiting for cloud connection (30 more seconds)..."
    sleep 30
    
    echo "✅ JDownloader should now be connected to MyJDownloader cloud"
    echo ""
    echo "You can verify the connection at: https://my.jdownloader.org"
else
    echo "❌ Failed to start JDownloader"
    exit 1
fi
