#!/bin/bash
# Test script for MyJDownloader Cloud Connection

echo "======================================================================"
echo "       Testing MyJDownloader Cloud Connection & Verification"
echo "======================================================================"
echo ""

echo "📡 Testing /health endpoint..."
curl -s 'http://localhost:8001/health' | jq .
echo ""

echo "======================================================================"
echo ""

echo "☁️  Testing /cloud/devices endpoint..."
echo "    This verifies the local JDownloader is connected to cloud"
echo ""
response=$(curl -s --location 'http://localhost:8001/cloud/devices' --header 'Accept: application/json')
echo "$response" | jq .
echo ""

# Parse the response to check connection status
connected=$(echo "$response" | jq -r '.connected')
device_count=$(echo "$response" | jq -r '.device_count')

echo "======================================================================"
echo ""

if [ "$connected" = "true" ]; then
    echo "✅ SUCCESS: Connected to MyJDownloader cloud"
    echo "📱 Devices found: $device_count"
    
    if [ "$device_count" -gt 0 ]; then
        echo ""
        echo "🔍 Device details:"
        echo "$response" | jq -r '.devices[] | "   • \(.name) - Status: \(.status)"'
    else
        echo ""
        echo "ℹ️  No devices connected yet. Make sure JDownloader is running"
        echo "   and connected to your MyJDownloader account."
    fi
else
    echo "❌ FAILED: Not connected to MyJDownloader cloud"
fi

echo ""
echo "======================================================================"
