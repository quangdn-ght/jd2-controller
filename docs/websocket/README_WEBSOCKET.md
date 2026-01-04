# 🌐 JDownloader WebSocket API

Real-time control and monitoring of JDownloader through MyJDownloader cloud using WebSocket technology.

## ✨ Features

- 🔌 **Real-time Communication** - WebSocket-based bidirectional communication
- 📥 **Download Management** - Add, start, pause, stop, and remove downloads
- 📊 **Live Monitoring** - Real-time progress updates and statistics
- 🔗 **Linkgrabber Control** - Manage pending downloads
- 🌐 **Multiple Clients** - Support for multiple simultaneous connections
- 🎨 **Web UI Included** - Beautiful browser-based control panel
- 🐍 **Python Client** - Ready-to-use Python client library
- 📚 **Well Documented** - Complete API documentation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/ght/project/jd2-controller
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Server

```bash
./start_websocket_api.sh
```

Or manually:

```bash
python3 websocket_api.py
```

### 3. Access the Web UI

Open your browser and navigate to:
- **Web UI**: http://localhost:8001/
- **API Docs**: http://localhost:8001/docs

### 4. Use the WebSocket API

Connect to: `ws://localhost:8001/ws`

## 📁 Project Structure

```
jd2-controller/
├── websocket_api.py                # FastAPI WebSocket server
├── jd_websocket_controller.py      # Controller module (myjdapi)
├── websocket_client_example.py     # Python client examples
├── websocket_client.html           # Browser web client
├── start_websocket_api.sh          # Quick start script
├── requirements.txt                # Dependencies
└── docs/
    └── WEBSOCKET_API_GUIDE.md     # Complete documentation
```

## 💻 Usage Examples

### Browser Client (Easiest)

1. Start the server: `./start_websocket_api.sh`
2. Open `websocket_client.html` in your browser
3. Click "Connect to JDownloader"
4. Start managing your downloads!

### Python Client

```python
import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8001/ws"
    
    async with websockets.connect(uri) as websocket:
        # Connect to JDownloader
        await websocket.send(json.dumps({"action": "connect"}))
        response = await websocket.recv()
        print(response)
        
        # Add download links
        await websocket.send(json.dumps({
            "action": "add_links",
            "links": ["https://example.com/file.zip"],
            "package_name": "My Downloads"
        }))
        response = await websocket.recv()
        print(response)
        
        # Start monitoring
        await websocket.send(json.dumps({
            "action": "start_monitoring",
            "interval": 2
        }))
        
        # Listen for updates
        for i in range(10):
            update = await websocket.recv()
            print(update)

asyncio.run(main())
```

Run the interactive examples:

```bash
python3 websocket_client_example.py
```

## 📡 WebSocket Commands

### Connection

```json
{"action": "connect"}
```

### Add Downloads

```json
{
    "action": "add_links",
    "links": ["url1", "url2"],
    "package_name": "Optional Name"
}
```

### Control Downloads

```json
{"action": "start"}          // Start all downloads
{"action": "pause"}          // Pause all downloads  
{"action": "stop"}           // Stop all downloads
```

### Query Operations

```json
{"action": "status"}         // Get overall status
{"action": "get_downloads"}  // List all downloads
{"action": "get_linkgrabber"} // List linkgrabber items
```

### Monitoring

```json
{
    "action": "start_monitoring",
    "interval": 2  // Update interval in seconds
}
```

```json
{"action": "stop_monitoring"}
```

### Remove Downloads

```json
{
    "action": "remove",
    "link_ids": [1, 2, 3],
    "package_ids": [1]
}
```

## 📊 Response Format

```json
{
    "type": "response",
    "action": "connect",
    "timestamp": "2026-01-04T10:30:00",
    "success": true,
    "message": "Connected successfully"
}
```

### Monitoring Updates

```json
{
    "type": "monitoring_update",
    "timestamp": "2026-01-04T10:30:00",
    "status": {
        "state": "RUNNING",
        "active_downloads": 3,
        "total_downloads": 5,
        "progress": 60.5,
        "total_bytes": 1073741824,
        "loaded_bytes": 650117120
    },
    "downloads": [...]
}
```

## 🛠️ API Endpoints

### WebSocket

- `ws://localhost:8001/ws` - Main WebSocket endpoint

### HTTP

- `GET /` - Web UI and documentation
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## 🎯 Use Cases

### 1. Remote Download Management

Control your JDownloader from anywhere with internet access through the MyJDownloader cloud.

### 2. Automation Scripts

Integrate with your automation workflows:

```python
# Auto-add downloads from a file
with open('download_list.txt') as f:
    links = [line.strip() for line in f]
    
await websocket.send(json.dumps({
    "action": "add_links",
    "links": links
}))
```

### 3. Monitoring Dashboard

Build custom monitoring dashboards that display real-time download statistics.

### 4. Mobile Apps

Create mobile apps that connect to your JDownloader through the WebSocket API.

### 5. Integration with Other Services

Connect JDownloader with other services like:
- Chat bots (Discord, Telegram)
- Home automation systems
- Custom web applications

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
MYJD_EMAIL=your_email@example.com
MYJD_PASSWORD=your_password
MYJD_DEVICE_NAME=JDownloader@root
```

### Server Settings

Edit `websocket_api.py` to change:

```python
uvicorn.run(
    app,
    host="0.0.0.0",    # Listen on all interfaces
    port=8001,          # Port number
    log_level="info"    # Logging level
)
```

## 🐛 Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
lsof -i :8001

# Kill existing process
pkill -f websocket_api.py
```

### Can't Connect to JDownloader

```bash
# Verify credentials
python3 verify_connection_v2.py

# Check JDownloader is running
ps aux | grep JDownloader

# Start JDownloader
./start_jd2.sh
```

### WebSocket Connection Failed

1. Check server is running: `curl http://localhost:8001/health`
2. Check firewall: `sudo ufw allow 8001`
3. Check logs: `tail -f /tmp/jd_websocket.log`

## 📚 Documentation

For complete documentation, see:
- [WEBSOCKET_API_GUIDE.md](docs/WEBSOCKET_API_GUIDE.md) - Complete API guide
- [CONNECTION_SUCCESS.md](docs/CONNECTION_SUCCESS.md) - Setup guide
- [README_MAIN.md](README_MAIN.md) - Main project documentation

## 🔒 Security Notes

⚠️ **Important**: This implementation is for local/trusted networks only.

For production use, implement:
- API key authentication
- WSS (WebSocket Secure) with TLS certificates
- Rate limiting
- Input validation
- User authentication and authorization

## 🎨 Web Client Features

The included HTML client provides:
- ✅ Modern, responsive design
- 📊 Real-time statistics dashboard
- 📥 Easy link management
- 📦 Download list with progress bars
- 📜 Console log viewer
- 🎯 One-click controls

## 🚦 System Requirements

- Python 3.8+
- JDownloader 2
- MyJDownloader account
- Linux/Windows/macOS
- Internet connection

## 📝 License

Part of the jd2-controller project.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Authentication system
- Additional monitoring metrics
- Mobile-optimized UI
- Docker containerization
- Systemd service files

## 📞 Support

For issues or questions:
1. Check the [troubleshooting guide](docs/WEBSOCKET_API_GUIDE.md#troubleshooting)
2. Review existing documentation
3. Check JDownloader logs

---

**Created**: January 4, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
