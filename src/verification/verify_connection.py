#!/usr/bin/env python3
"""Verify JDownloader connection to MyJDownloader cloud"""
import os
import sys
from dotenv import load_dotenv
from src.jdownloader.jd_cloud_connector import MyJDownloaderAPI
from src.jdownloader.jd_auth_config import JDownloaderConfig

load_dotenv()

def verify_connection():
    """Verify connection and display results"""
    print("="*70)
    print("MyJDownloader Cloud Connection Verification")
    print("="*70)
    
    # Get credentials from config
    jd = JDownloaderConfig()
    config = jd.read_config()
    
    email = config.get("email")
    password = config.get("password")
    device_name = config.get("devicename", "Unknown")
    
    if not email or not password:
        print("❌ Error: No credentials configured")
        print("   Please configure credentials first:")
        print("   python jd_auth_config.py --email YOUR_EMAIL --password YOUR_PASSWORD")
        return False
    
    print(f"\n📧 Email: {email}")
    print(f"🖥️  Expected Device: {device_name}")
    print("\n🔍 Checking connection to MyJDownloader cloud...")
    
    # Create API client
    api = MyJDownloaderAPI(email, password)
    
    # Try to connect
    success, message = api.connect()
    if not success:
        print(f"❌ Connection failed: {message}")
        return False
    
    print(f"✅ Connected to MyJDownloader API")
    
    # List devices
    print("\n📱 Listing connected devices...")
    success, devices, message = api.list_devices()
    
    if not success:
        print(f"❌ Failed to list devices: {message}")
        return False
    
    if not devices:
        print("⚠️  No devices found connected to MyJDownloader cloud")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure JDownloader is running: ps aux | grep JDownloader")
        print("   2. Check JDownloader logs: tail -f /tmp/jd2.log")
        print("   3. Wait 1-2 minutes for the connection to establish")
        print("   4. Verify credentials are correct in JDownloader config")
        return False
    
    print(f"\n✅ Found {len(devices)} device(s) connected:")
    print("-"*70)
    
    device_found = False
    for i, device in enumerate(devices, 1):
        name = device.get("name", "Unknown")
        device_id = device.get("id", "N/A")
        device_type = device.get("type", "N/A")
        status = device.get("status", "OFFLINE")
        
        is_expected = name.lower() == device_name.lower()
        if is_expected:
            device_found = True
        
        marker = "✅" if is_expected else "  "
        print(f"{marker} Device {i}:")
        print(f"   Name:   {name}")
        print(f"   ID:     {device_id}")
        print(f"   Type:   {device_type}")
        print(f"   Status: {status}")
        print()
    
    if device_found:
        print("="*70)
        print("🎉 SUCCESS! Your JDownloader is connected to the cloud!")
        print("="*70)
        return True
    else:
        print("="*70)
        print("⚠️  Device found but name doesn't match expected device")
        print(f"   Expected: {device_name}")
        print(f"   Found: {', '.join([d.get('name', 'Unknown') for d in devices])}")
        print("="*70)
        return True

if __name__ == "__main__":
    try:
        success = verify_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
