#!/usr/bin/env python3
"""WebSocket API Server for JDownloader Control"""
import asyncio
import json
from typing import Dict, Set
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.jdownloader.jd_websocket_controller import JDownloaderWebSocketController


app = FastAPI(
    title="JDownloader WebSocket API",
    description="Real-time WebSocket API for controlling JDownloader through MyJDownloader cloud",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.controller = JDownloaderWebSocketController()
        self.monitoring_task = None
        
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        await websocket.send_json(message)
        
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSockets"""
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except Exception:
                self.active_connections.discard(connection)
    
    async def start_monitoring(self, interval: int = 2):
        """Start monitoring downloads and broadcast updates"""
        while self.active_connections and self.controller.connected:
            try:
                # Get current download status
                status = await self.controller.get_download_status()
                
                # Get detailed downloads
                downloads = await self.controller.get_downloads()
                
                # Prepare monitoring update
                update = {
                    "type": "monitoring_update",
                    "timestamp": datetime.now().isoformat(),
                    "status": status,
                    "downloads": downloads.get("downloads", []) if downloads.get("success") else []
                }
                
                # Broadcast to all clients
                await self.broadcast(update)
                
                # Wait before next update
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(interval)


# Global connection manager
manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_root():
    """Root endpoint with API information"""
    return """
    <html>
        <head>
            <title>JDownloader WebSocket API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007bff; }
                code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
                .section { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 JDownloader WebSocket API</h1>
                <p>Real-time control and monitoring for JDownloader through MyJDownloader cloud</p>
                
                <div class="section">
                    <h2>WebSocket Endpoint</h2>
                    <div class="endpoint">
                        <strong>WS:</strong> <code>ws://localhost:8001/ws</code>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Available Commands</h2>
                    
                    <div class="endpoint">
                        <strong>Connect:</strong><br>
                        <code>{"action": "connect"}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Add Links:</strong><br>
                        <code>{"action": "add_links", "links": ["url1", "url2"], "package_name": "My Package"}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Get Downloads:</strong><br>
                        <code>{"action": "get_downloads"}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Get Linkgrabber:</strong><br>
                        <code>{"action": "get_linkgrabber"}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Start Downloads:</strong><br>
                        <code>{"action": "start", "link_ids": [1, 2, 3]}</code> (optional link_ids)
                    </div>
                    
                    <div class="endpoint">
                        <strong>Pause Downloads:</strong><br>
                        <code>{"action": "pause", "link_ids": [1, 2]}</code> (optional link_ids)
                    </div>
                    
                    <div class="endpoint">
                        <strong>Stop Downloads:</strong><br>
                        <code>{"action": "stop"}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Remove Links:</strong><br>
                        <code>{"action": "remove", "link_ids": [1, 2], "package_ids": [1]}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Move to Downloads:</strong><br>
                        <code>{"action": "move_to_downloads", "link_ids": [1, 2], "package_ids": [1]}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Get Status:</strong><br>
                        <code>{"action": "status"}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Start Monitoring:</strong><br>
                        <code>{"action": "start_monitoring", "interval": 2}</code>
                    </div>
                    
                    <div class="endpoint">
                        <strong>Stop Monitoring:</strong><br>
                        <code>{"action": "stop_monitoring"}</code>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📱 Try the Interactive Demo</h2>
                    <p>
                        <a href="/demo" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                            🚀 Launch Web Client Demo
                        </a>
                    </p>
                    <p style="color: #666; font-size: 14px; margin-top: 10px;">
                        Try the interactive web interface to control JDownloader with a beautiful UI
                    </p>
                </div>
                
                <div class="section">
                    <h2>Documentation</h2>
                    <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/demo", response_class=HTMLResponse)
async def get_demo():
    """Serve the interactive web client demo"""
    html_file = Path(__file__).parent.parent / "client" / "websocket_client.html"
    
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Demo client not found")
    
    return FileResponse(html_file)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for JDownloader control.
    
    Accepts JSON commands and returns JSON responses.
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "welcome",
            "message": "Connected to JDownloader WebSocket API",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                command = json.loads(data)
                action = command.get("action")
                
                if not action:
                    await manager.send_personal_message({
                        "type": "error",
                        "error": "No action specified"
                    }, websocket)
                    continue
                
                # Process action
                response = await process_action(action, command, manager)
                
                # Send response
                await manager.send_personal_message(response, websocket)
                
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "error": "Invalid JSON format"
                }, websocket)
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "error": str(e)
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected")


async def process_action(action: str, command: dict, manager: ConnectionManager) -> dict:
    """
    Process WebSocket action commands.
    
    Args:
        action: Action to perform
        command: Full command dictionary with parameters
        manager: Connection manager instance
    
    Returns:
        Response dictionary
    """
    controller = manager.controller
    
    # Connect action
    if action == "connect":
        result = await controller.connect()
        return {
            "type": "response",
            "action": "connect",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Disconnect action
    elif action == "disconnect":
        result = await controller.disconnect()
        return {
            "type": "response",
            "action": "disconnect",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Add links action
    elif action == "add_links":
        links = command.get("links", [])
        package_name = command.get("package_name")
        result = await controller.add_links(links, package_name)
        return {
            "type": "response",
            "action": "add_links",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Get downloads action
    elif action == "get_downloads":
        result = await controller.get_downloads()
        return {
            "type": "response",
            "action": "get_downloads",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Get linkgrabber action
    elif action == "get_linkgrabber":
        result = await controller.get_linkgrabber()
        return {
            "type": "response",
            "action": "get_linkgrabber",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Start downloads action
    elif action == "start":
        link_ids = command.get("link_ids")
        result = await controller.start_downloads(link_ids)
        return {
            "type": "response",
            "action": "start",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Pause downloads action
    elif action == "pause":
        link_ids = command.get("link_ids")
        result = await controller.pause_downloads(link_ids)
        return {
            "type": "response",
            "action": "pause",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Stop downloads action
    elif action == "stop":
        result = await controller.stop_downloads()
        return {
            "type": "response",
            "action": "stop",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Remove links action
    elif action == "remove":
        link_ids = command.get("link_ids", [])
        package_ids = command.get("package_ids", [])
        result = await controller.remove_links(link_ids, package_ids)
        return {
            "type": "response",
            "action": "remove",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Move to downloads action
    elif action == "move_to_downloads":
        link_ids = command.get("link_ids")
        package_ids = command.get("package_ids")
        result = await controller.move_to_downloads(link_ids, package_ids)
        return {
            "type": "response",
            "action": "move_to_downloads",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Get status action
    elif action == "status":
        result = await controller.get_download_status()
        return {
            "type": "response",
            "action": "status",
            "timestamp": datetime.now().isoformat(),
            **result
        }
    
    # Start monitoring action
    elif action == "start_monitoring":
        interval = command.get("interval", 2)
        
        # Cancel existing monitoring task if any
        if manager.monitoring_task and not manager.monitoring_task.done():
            manager.monitoring_task.cancel()
        
        # Start new monitoring task
        manager.monitoring_task = asyncio.create_task(manager.start_monitoring(interval))
        
        return {
            "type": "response",
            "action": "start_monitoring",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "message": f"Monitoring started with {interval}s interval"
        }
    
    # Stop monitoring action
    elif action == "stop_monitoring":
        if manager.monitoring_task and not manager.monitoring_task.done():
            manager.monitoring_task.cancel()
        
        return {
            "type": "response",
            "action": "stop_monitoring",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "message": "Monitoring stopped"
        }
    
    # Unknown action
    else:
        return {
            "type": "error",
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "error": f"Unknown action: {action}"
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "JDownloader WebSocket API",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Starting JDownloader WebSocket API Server...")
    print("📡 WebSocket endpoint: ws://localhost:8001/ws")
    print("🎨 Demo Client: http://localhost:8001/demo")
    print("📚 Documentation: http://localhost:8001/docs")
    print("🌐 Web UI: http://localhost:8001/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
