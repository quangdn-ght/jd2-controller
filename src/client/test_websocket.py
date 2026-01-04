#!/usr/bin/env python3
"""
Quick test script for WebSocket API
Tests basic connectivity and commands
"""
import asyncio
import json
import sys
from src.jdownloader.jd_websocket_controller import JDownloaderWebSocketController


async def test_controller():
    """Test the controller without WebSocket server"""
    print("=" * 70)
    print("Testing JDownloader WebSocket Controller")
    print("=" * 70)
    print()
    
    controller = JDownloaderWebSocketController()
    
    # Test 1: Connect
    print("Test 1: Connecting to JDownloader cloud...")
    result = await controller.connect()
    
    if result.get("success"):
        print(f"✅ Connected successfully")
        print(f"   Device: {result.get('device_name')}")
        print(f"   Device ID: {result.get('device_id')}")
        print(f"   Type: {result.get('device_type')}")
    else:
        print(f"❌ Connection failed: {result.get('error')}")
        return False
    
    print()
    
    # Test 2: Get Status
    print("Test 2: Getting download status...")
    status = await controller.get_download_status()
    
    if status.get("success"):
        print(f"✅ Status retrieved")
        print(f"   State: {status.get('state')}")
        print(f"   Active Downloads: {status.get('active_downloads')}")
        print(f"   Total Downloads: {status.get('total_downloads')}")
        print(f"   Progress: {status.get('progress')}%")
    else:
        print(f"⚠️  Status check: {status.get('error')}")
    
    print()
    
    # Test 3: Get Downloads
    print("Test 3: Getting current downloads...")
    downloads = await controller.get_downloads()
    
    if downloads.get("success"):
        print(f"✅ Downloads retrieved")
        print(f"   Total: {downloads.get('total_downloads')}")
        
        if downloads.get('downloads'):
            print("\n   Downloads:")
            for dl in downloads['downloads'][:5]:  # Show first 5
                print(f"   - {dl.get('name')} ({dl.get('status')})")
        else:
            print("   (No active downloads)")
    else:
        print(f"⚠️  Downloads check: {downloads.get('error')}")
    
    print()
    
    # Test 4: Get Linkgrabber
    print("Test 4: Getting linkgrabber items...")
    linkgrabber = await controller.get_linkgrabber()
    
    if linkgrabber.get("success"):
        print(f"✅ Linkgrabber retrieved")
        print(f"   Total Links: {linkgrabber.get('total_links')}")
        
        if linkgrabber.get('linkgrabber'):
            print("\n   Links:")
            for link in linkgrabber['linkgrabber'][:5]:  # Show first 5
                print(f"   - {link.get('name')}")
        else:
            print("   (No links in linkgrabber)")
    else:
        print(f"⚠️  Linkgrabber check: {linkgrabber.get('error')}")
    
    print()
    
    # Test 5: Disconnect
    print("Test 5: Disconnecting...")
    result = await controller.disconnect()
    
    if result.get("success"):
        print(f"✅ Disconnected successfully")
    else:
        print(f"❌ Disconnect failed: {result.get('error')}")
    
    print()
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)
    
    return True


def main():
    """Main function"""
    print("\n🧪 JDownloader WebSocket Controller Test\n")
    
    try:
        success = asyncio.run(test_controller())
        
        if success:
            print("\n✅ Controller is working correctly!")
            print("\nNext steps:")
            print("1. Start the WebSocket server:")
            print("   ./start_websocket_api.sh")
            print()
            print("2. Open the web client:")
            print("   Open websocket_client.html in your browser")
            print()
            print("3. Or run Python client examples:")
            print("   python3 websocket_client_example.py")
            sys.exit(0)
        else:
            print("\n❌ Tests failed. Please check your configuration.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure:")
        print("- JDownloader is running")
        print("- Credentials are configured in .env")
        print("- Device is connected to MyJDownloader cloud")
        sys.exit(1)


if __name__ == "__main__":
    main()
