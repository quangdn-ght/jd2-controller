#!/usr/bin/env python3
"""
WebSocket Client Example for JDownloader Control

This script demonstrates how to connect to the JDownloader WebSocket API
and perform various download management operations.
"""
import asyncio
import json
import websockets
from datetime import datetime


class JDownloaderWebSocketClient:
    """Simple WebSocket client for JDownloader API"""
    
    def __init__(self, uri: str = "ws://localhost:8001/ws"):
        self.uri = uri
        self.websocket = None
        
    async def connect(self):
        """Connect to WebSocket server"""
        print(f"🔌 Connecting to {self.uri}...")
        self.websocket = await websockets.connect(self.uri)
        print("✅ Connected!")
        
        # Receive welcome message
        welcome = await self.websocket.recv()
        print(f"📨 {welcome}\n")
        
    async def send_command(self, command: dict):
        """Send a command and wait for response"""
        if not self.websocket:
            raise Exception("Not connected")
        
        print(f"📤 Sending: {json.dumps(command, indent=2)}")
        await self.websocket.send(json.dumps(command))
        
        # Wait for response
        response = await self.websocket.recv()
        response_data = json.loads(response)
        print(f"📥 Response: {json.dumps(response_data, indent=2)}\n")
        
        return response_data
    
    async def listen(self, duration: int = 10):
        """Listen for messages for a specified duration"""
        print(f"👂 Listening for {duration} seconds...")
        
        try:
            end_time = asyncio.get_event_loop().time() + duration
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    # Wait for message with timeout
                    remaining = end_time - asyncio.get_event_loop().time()
                    if remaining <= 0:
                        break
                    
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=min(1.0, remaining)
                    )
                    
                    data = json.loads(message)
                    
                    # Handle different message types
                    if data.get("type") == "monitoring_update":
                        print(f"📊 Monitoring Update [{data.get('timestamp')}]:")
                        status = data.get("status", {})
                        print(f"   State: {status.get('state')}")
                        print(f"   Active Downloads: {status.get('active_downloads')}")
                        print(f"   Progress: {status.get('progress')}%")
                        print(f"   Total Downloads: {status.get('total_downloads')}\n")
                    else:
                        print(f"📨 {json.dumps(data, indent=2)}\n")
                        
                except asyncio.TimeoutError:
                    continue
                    
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
    
    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()
            print("👋 Disconnected")


async def example_basic_usage():
    """Example: Basic usage - connect and get status"""
    print("=" * 70)
    print("Example 1: Basic Usage")
    print("=" * 70 + "\n")
    
    client = JDownloaderWebSocketClient()
    
    try:
        # Connect to server
        await client.connect()
        
        # Connect to JDownloader cloud
        await client.send_command({"action": "connect"})
        
        # Get download status
        await client.send_command({"action": "status"})
        
        # Get current downloads
        await client.send_command({"action": "get_downloads"})
        
        # Disconnect
        await client.send_command({"action": "disconnect"})
        
    finally:
        await client.close()


async def example_add_and_monitor():
    """Example: Add links and monitor downloads"""
    print("=" * 70)
    print("Example 2: Add Links and Monitor")
    print("=" * 70 + "\n")
    
    client = JDownloaderWebSocketClient()
    
    try:
        # Connect
        await client.connect()
        
        # Connect to JDownloader
        await client.send_command({"action": "connect"})
        
        # Add download links (example URLs - replace with actual URLs)
        await client.send_command({
            "action": "add_links",
            "links": [
                "https://example.com/file1.zip",
                "https://example.com/file2.zip"
            ],
            "package_name": "Example Package"
        })
        
        # Get linkgrabber
        await client.send_command({"action": "get_linkgrabber"})
        
        # Start monitoring
        await client.send_command({
            "action": "start_monitoring",
            "interval": 2
        })
        
        # Listen for monitoring updates
        await client.listen(duration=10)
        
        # Stop monitoring
        await client.send_command({"action": "stop_monitoring"})
        
    finally:
        await client.close()


async def example_download_control():
    """Example: Control downloads (start, pause, stop)"""
    print("=" * 70)
    print("Example 3: Download Control")
    print("=" * 70 + "\n")
    
    client = JDownloaderWebSocketClient()
    
    try:
        # Connect
        await client.connect()
        
        # Connect to JDownloader
        await client.send_command({"action": "connect"})
        
        # Start all downloads
        await client.send_command({"action": "start"})
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Get status
        await client.send_command({"action": "status"})
        
        # Pause all downloads
        await client.send_command({"action": "pause"})
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Resume downloads
        await client.send_command({"action": "start"})
        
        # Stop all downloads
        await client.send_command({"action": "stop"})
        
    finally:
        await client.close()


async def example_interactive():
    """Interactive mode - send custom commands"""
    print("=" * 70)
    print("Interactive Mode")
    print("=" * 70 + "\n")
    print("Available commands:")
    print("  connect              - Connect to JDownloader cloud")
    print("  status               - Get download status")
    print("  downloads            - List current downloads")
    print("  linkgrabber          - List linkgrabber items")
    print("  start                - Start downloads")
    print("  pause                - Pause downloads")
    print("  stop                 - Stop downloads")
    print("  monitor <seconds>    - Monitor for specified seconds")
    print("  quit                 - Exit")
    print()
    
    client = JDownloaderWebSocketClient()
    
    try:
        await client.connect()
        
        while True:
            try:
                # Get user input
                user_input = input("Command> ").strip().lower()
                
                if not user_input:
                    continue
                
                if user_input == "quit":
                    break
                
                # Parse command
                parts = user_input.split()
                command = parts[0]
                
                # Execute command
                if command == "connect":
                    await client.send_command({"action": "connect"})
                
                elif command == "status":
                    await client.send_command({"action": "status"})
                
                elif command == "downloads":
                    await client.send_command({"action": "get_downloads"})
                
                elif command == "linkgrabber":
                    await client.send_command({"action": "get_linkgrabber"})
                
                elif command == "start":
                    await client.send_command({"action": "start"})
                
                elif command == "pause":
                    await client.send_command({"action": "pause"})
                
                elif command == "stop":
                    await client.send_command({"action": "stop"})
                
                elif command == "monitor":
                    duration = int(parts[1]) if len(parts) > 1 else 10
                    await client.send_command({
                        "action": "start_monitoring",
                        "interval": 2
                    })
                    await client.listen(duration)
                    await client.send_command({"action": "stop_monitoring"})
                
                else:
                    print(f"❌ Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        await client.close()


async def main():
    """Main function - select example to run"""
    print("\n" + "=" * 70)
    print("JDownloader WebSocket Client Examples")
    print("=" * 70 + "\n")
    
    print("Select an example to run:")
    print("1. Basic Usage (connect and get status)")
    print("2. Add Links and Monitor")
    print("3. Download Control (start/pause/stop)")
    print("4. Interactive Mode")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    print()
    
    if choice == "1":
        await example_basic_usage()
    elif choice == "2":
        await example_add_and_monitor()
    elif choice == "3":
        await example_download_control()
    elif choice == "4":
        await example_interactive()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
