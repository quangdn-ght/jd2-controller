#!/usr/bin/env python3
"""Verify JDownloader connection to MyJDownloader cloud using official myjdapi"""
import os
import sys
from dotenv import load_dotenv
from jd_auth_config import JDownloaderConfig
import myjdapi

load_dotenv()

def verify_with_official_api():
    """Verify connection using official myjdapi library"""
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
    print("\n🔍 Connecting to MyJDownloader cloud...")
    
    try:
        # Create  API client
        jd_api = myjdapi.Myjdapi()
        jd_api.set_app_key("jd2controller")
        
        # Connect
        jd_api.connect(email, password)
        print("✅ Connected to MyJDownloader API")
        
        # Update devices
        print("\n📱 Fetching connected devices...")
        jd_api.update_devices()
        devices = jd_api.list_devices()
        
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
            
            is_expected = name.lower() == device_name.lower() or name in device_name or device_name in name
            if is_expected:
                device_found = True
            
            marker = "✅" if is_expected else "  "
            print(f"{marker} Device {i}:")
            print(f"   Name:   {name}")
            print(f"   ID:     {device_id}")
            print(f"   Type:   {device_type}")
            print(f"   Status: {status}")
            print()
        
        if device_found or len(devices) > 0:
            print("="*70)
            print("🎉 SUCCESS! JDownloader is connected to MyJDownloader cloud!")
            print("="*70)
            if not device_found and len(devices) > 0:
                print(f"\n💡 Note: Expected device '{device_name}' not found by exact match,")
                print(f"   but {len(devices)} device(s) are connected.")
            return True
        else:
            print("="*70)
            print("⚠️  No matching device found")
            print(f"   Expected: {device_name}")
            print("="*70)
            return False
            
    except myjdapi.exception.MYJDException as e:
        print(f"❌ MyJDownloader API Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = verify_with_official_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
