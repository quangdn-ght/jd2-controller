# 🌐 JDownloader WebSocket API - Quick Start Guide

## Overview

This WebSocket API provides real-time control and monitoring of JDownloader through MyJDownloader cloud. It allows you to:

- ✅ Add download links
- ▶️ Start/Pause/Stop downloads
- 📊 Monitor download progress in real-time
- 🔗 Manage linkgrabber
- 📦 Control download packages
- 🗑️ Remove downloads

## Installation

### 1. Install Dependencies

```bash
cd /home/ght/project/jd2-controller
source venv/bin/activate
pip install -r requirements.txt
```

Required packages:
- `myjdapi` - Official MyJDownloader API client
- `fastapi` - WebSocket server framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket client support

### 2. Configure Credentials

Make sure your JDownloader credentials are configured in `.env`:

```bash
MYJD_EMAIL=quangdn@giahungtech.com.vn
MYJD_PASSWORD=your_password
MYJD_DEVICE_NAME=JDownloader@root
```

Or use the config script:

```bash
python jd_auth_config.py --email YOUR_EMAIL --password YOUR_PASSWORD
```

## Starting the Server

### Method 1: Direct Start

```bash
cd /home/ght/project/jd2-controller
source venv/bin/activate
python websocket_api.py
```

The server will start on:
- � **Demo Client**: http://localhost:8001/demo
- �🌐 Web UI: http://localhost:8001/
- 📡 WebSocket: ws://localhost:8001/ws
- 📚 API Docs: http://localhost:8001/docs

### Method 2: Background Process

```bash
cd /home/ght/project/jd2-controller
source venv/bin/activate
nohup python websocket_api.py > /tmp/jd_websocket.log 2>&1 &
```

Check logs:
```bash
tail -f /tmp/jd_websocket.log
```

Stop server:
```bash
pkill -f websocket_api.py
```

## Usage Examples

### 1. Browser Client (Easiest)

1. Start the WebSocket server
2. Open [websocket_client.html](websocket_client.html) in your browser
3. Click "Connect to JDownloader"
4. Use the web interface to control downloads

**Features:**
- 🎨 Modern, responsive UI
- 📊 Real-time monitoring with statistics
- 📥 Easy link management
- 📜 Console log viewer

### 2. Python Client

Run the interactive example:

```bash
python websocket_client_example.py
```

Select from examples:
1. **Basic Usage** - Connect and get status
2. **Add Links and Monitor** - Add downloads and monitor progress
3. **Download Control** - Start/pause/stop operations
4. **Interactive Mode** - Manual command entry

### 3. Custom Python Integration

```python
import asyncio
import json
import websockets

async def control_jdownloader():
    uri = "ws://localhost:8001/ws"
    
    async with websockets.connect(uri) as websocket:
        # Connect to JDownloader
        await websocket.send(json.dumps({"action": "connect"}))
        response = await websocket.recv()
        print(response)
        
        # Add download links
        await websocket.send(json.dumps({
            "action": "add_links",
            "links": [
                "https://example.com/file1.zip",
                "https://example.com/file2.zip"
            ],
            "package_name": "My Downloads"
        }))
        response = await websocket.recv()
        print(response)
        
        # Start downloads
        await websocket.send(json.dumps({"action": "start"}))
        response = await websocket.recv()
        print(response)

asyncio.run(control_jdownloader())
```

### 4. JavaScript/Node.js Client

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8001/ws');

ws.on('open', () => {
    console.log('Connected');
    
    // Connect to JDownloader
    ws.send(JSON.stringify({ action: 'connect' }));
});

ws.on('message', (data) => {
    const message = JSON.parse(data);
    console.log('Received:', message);
    
    if (message.type === 'monitoring_update') {
        console.log('Progress:', message.status.progress + '%');
    }
});

// Add links
ws.send(JSON.stringify({
    action: 'add_links',
    links: ['https://example.com/file.zip'],
    package_name: 'Test Package'
}));

// Start monitoring
ws.send(JSON.stringify({
    action: 'start_monitoring',
    interval: 2
}));
```

## WebSocket Commands

All commands are sent as JSON objects with an `action` field.

### Connection Management

**Connect to JDownloader:**
```json
{"action": "connect"}
```

**Disconnect:**
```json
{"action": "disconnect"}
```

### Adding Downloads

**Add Links:**
```json
{
    "action": "add_links",
    "links": ["url1", "url2", "url3"],
    "package_name": "Optional Package Name"
}
```

### Download Control

**Start All Downloads:**
```json
{"action": "start"}
```

**Start Specific Downloads:**
```json
{
    "action": "start",
    "link_ids": [1, 2, 3]
}
```

**Pause All Downloads:**
```json
{"action": "pause"}
```

**Pause Specific Downloads:**
```json
{
    "action": "pause",
    "link_ids": [1, 2]
}
```

**Stop All Downloads:**
```json
{"action": "stop"}
```

### Query Operations

**Get Download Status:**
```json
{"action": "status"}
```

Response includes:
- Current state (running/stopped/paused)
- Active downloads count
- Total downloads
- Progress percentage
- Bytes loaded/total

**Get All Downloads:**
```json
{"action": "get_downloads"}
```

**Get Linkgrabber Items:**
```json
{"action": "get_linkgrabber"}
```

### Remove Operations

**Remove Links:**
```json
{
    "action": "remove",
    "link_ids": [1, 2, 3],
    "package_ids": [1]
}
```

### Linkgrabber Operations

**Move Links to Downloads:**
```json
{
    "action": "move_to_downloads",
    "link_ids": [1, 2],
    "package_ids": [1]
}
```

### Real-time Monitoring

**Start Monitoring:**
```json
{
    "action": "start_monitoring",
    "interval": 2
}
```

This will broadcast updates every 2 seconds with:
- Download status
- Active downloads
- Progress information
- Current download list

**Stop Monitoring:**
```json
{"action": "stop_monitoring"}
```

## Response Format

All responses are JSON objects with these common fields:

```json
{
    "type": "response",
    "action": "the_action_you_sent",
    "timestamp": "2026-01-04T10:30:00",
    "success": true,
    "message": "Optional success message",
    "error": "Optional error message if success is false"
}
```

### Monitoring Updates

When monitoring is active, you'll receive periodic updates:

```json
{
    "type": "monitoring_update",
    "timestamp": "2026-01-04T10:30:00",
    "status": {
        "success": true,
        "state": "RUNNING",
        "active_downloads": 3,
        "total_downloads": 5,
        "total_bytes": 1073741824,
        "loaded_bytes": 536870912,
        "progress": 50.0
    },
    "downloads": [
        {
            "name": "file1.zip",
            "status": "Downloading",
            "bytesTotal": 104857600,
            "bytesLoaded": 52428800,
            "speed": 1048576,
            "eta": 50,
            "enabled": true,
            "finished": false,
            "uuid": "abc123",
            "url": "https://example.com/file1.zip"
        }
    ]
}
```

## Architecture

```
┌─────────────────┐
│  Your Client    │
│  (Browser/App)  │
└────────┬────────┘
         │ WebSocket
         │
┌────────▼────────┐
│ websocket_api.py│
│  FastAPI Server │
└────────┬────────┘
         │
┌────────▼─────────────────┐
│ jd_websocket_controller  │
│  (myjdapi integration)   │
└────────┬─────────────────┘
         │ HTTPS API
         │
┌────────▼────────────┐
│  MyJDownloader      │
│  Cloud Service      │
└────────┬────────────┘
         │ Internet
         │
┌────────▼────────────┐
│   JDownloader       │
│   Local Instance    │
└─────────────────────┘
```

## Files Overview

- **websocket_api.py** - FastAPI WebSocket server
- **jd_websocket_controller.py** - Controller module using myjdapi
- **websocket_client_example.py** - Python client examples
- **websocket_client.html** - Browser-based web client
- **requirements.txt** - Python dependencies

## Troubleshooting

### Server Won't Start

**Check if port is already in use:**
```bash
lsof -i :8001
```

**Kill existing process:**
```bash
pkill -f websocket_api.py
```

### Connection Failed

1. **Verify JDownloader is running:**
   ```bash
   ps aux | grep JDownloader
   ```

2. **Check credentials:**
   ```bash
   python verify_connection_v2.py
   ```

3. **Verify MyJDownloader connection:**
   - Visit https://my.jdownloader.org
   - Check if your device is online

### WebSocket Connection Issues

1. **Check server is running:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Check firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 8001
   ```

3. **Check logs:**
   ```bash
   tail -f /tmp/jd_websocket.log
   ```

### No Downloads Showing

1. **Connect first:**
   Send `{"action": "connect"}` before other commands

2. **Check linkgrabber:**
   Use `{"action": "get_linkgrabber"}` to see pending links

3. **Move to downloads:**
   Links must be moved from linkgrabber to downloads

## Advanced Features

### Custom Monitoring Interval

Adjust the monitoring update frequency (in seconds):

```json
{
    "action": "start_monitoring",
    "interval": 5
}
```

Lower values = more frequent updates = more network usage

### Multiple Clients

The server supports multiple simultaneous WebSocket connections. All connected clients receive monitoring updates when monitoring is active.

### Error Handling

All operations return success/failure status. Always check the `success` field:

```javascript
ws.on('message', (data) => {
    const response = JSON.parse(data);
    
    if (response.success) {
        console.log('Success:', response.message);
    } else {
        console.error('Error:', response.error);
    }
});
```

## Security Considerations

⚠️ **Important**: This implementation does not include authentication. For production use:

1. Add API key authentication
2. Use WSS (WebSocket Secure) with TLS
3. Implement rate limiting
4. Add user authentication
5. Use environment variables for sensitive data

## Next Steps

1. ✅ Start the WebSocket server
2. ✅ Open the HTML client in your browser
3. ✅ Connect to JDownloader
4. ✅ Start adding and managing downloads!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review [CONNECTION_SUCCESS.md](CONNECTION_SUCCESS.md)
3. Check JDownloader logs: `/tmp/jd2.log`

---

**Created**: January 4, 2026  
**Version**: 1.0.0
