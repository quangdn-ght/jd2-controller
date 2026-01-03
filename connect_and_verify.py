#!/usr/bin/env python3
"""
Complete JDownloader Cloud Connection Script
Handles starting JDownloader and verifying cloud connection
"""
import os
import sys
import time
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")

def check_jdownloader_running():
    """Check if JDownloader is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "JDownloader.jar"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return True, [int(pid) for pid in pids if pid]
        return False, []
    except Exception as e:
        print(f"Error checking process: {e}")
        return False, []

def start_jdownloader():
    """Start JDownloader service"""
    print_header("STEP 1: Starting JDownloader")
    
    # Check if already running
    is_running, pids = check_jdownloader_running()
    if is_running:
        print(f"✅ JDownloader is already running (PIDs: {', '.join(map(str, pids))})")
        return True
    
    # Check if JAR exists
    jar_path = Path("/opt/jd2/JDownloader.jar")
    if not jar_path.exists():
        print(f"❌ Error: JDownloader.jar not found at {jar_path}")
        return False
    
    print("🚀 Starting JDownloader...")
    try:
        # Kill any zombie processes
        subprocess.run(["sudo", "pkill", "-9", "-f", "JDownloader.jar"], 
                      capture_output=True)
        time.sleep(2)
        
        # Start JDownloader
        subprocess.Popen(
            ["sudo", "nohup", "java", "-jar", str(jar_path), "-norestart"],
            cwd="/opt/jd2",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Wait and verify
        print("⏳ Waiting for JDownloader to start (10 seconds)...")
        time.sleep(10)
        
        is_running, pids = check_jdownloader_running()
        if is_running:
            print(f"✅ JDownloader started successfully (PIDs: {', '.join(map(str, pids))})")
            print("📝 Logs available at: /tmp/jd2.log")
            return True
        else:
            print("❌ Failed to start JDownloader")
            return False
            
    except Exception as e:
        print(f"❌ Error starting JDownloader: {e}")
        return False

def verify_cloud_connection():
    """Verify cloud connection using official API"""
    print_header("STEP 2: Verifying Cloud Connection")
    
    try:
        # Import here to avoid issues if not installed
        from dotenv import load_dotenv
        from jd_auth_config import JDownloaderConfig
        import myjdapi
        
        load_dotenv()
        
        # Get credentials
        jd = JDownloaderConfig()
        config = jd.read_config()
        
        email = config.get("email")
        password = config.get("password")
        device_name = config.get("devicename", "Unknown")
        
        if not email or not password:
            print("❌ Error: No credentials configured")
            print("   Run: python jd_auth_config.py --email EMAIL --password PASSWORD")
            return False
        
        print(f"📧 Email: {email}")
        print(f"🖥️  Expected Device: {device_name}")
        print("\n🔍 Connecting to MyJDownloader cloud...")
        
        # Create API client
        jd_api = myjdapi.Myjdapi()
        jd_api.set_app_key("jd2controller")
        
        # Connect
        jd_api.connect(email, password)
        print("✅ Connected to MyJDownloader API")
        
        # Get devices
        print("\n📱 Fetching connected devices...")
        jd_api.update_devices()
        devices = jd_api.list_devices()
        
        if not devices:
            print("\n⚠️  No devices found connected to cloud")
            print("\n💡 Troubleshooting:")
            print("   1. Wait 1-2 minutes for initial connection")
            print("   2. Check logs: tail -f /tmp/jd2.log")
            print("   3. Verify credentials in config")
            return False
        
        print(f"\n✅ Found {len(devices)} device(s) connected:")
        print("-"*70)
        
        device_found = False
        for i, device in enumerate(devices, 1):
            name = device.get("name", "Unknown")
            device_id = device.get("id", "N/A")
            status = device.get("status", "UNKNOWN")
            
            is_match = (name.lower() == device_name.lower() or 
                       device_name in name or 
                       name in device_name)
            
            if is_match:
                device_found = True
            
            marker = "✅" if is_match else "  "
            print(f"{marker} Device {i}:")
            print(f"   Name:   {name}")
            print(f"   ID:     {device_id}")
            print(f"   Status: {status}")
            print()
        
        if devices:
            print("="*70)
            print("🎉 SUCCESS! JDownloader is connected to the cloud!")
            print("="*70)
            print("\n🌐 Access your downloads at: https://my.jdownloader.org")
            return True
        
        return False
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install myjdapi python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main execution"""
    print_header("JDownloader Cloud Connection")
    print("This script will:")
    print("  1. Start JDownloader (if not running)")
    print("  2. Verify connection to MyJDownloader cloud")
    print()
    
    # Step 1: Start JDownloader
    if not start_jdownloader():
        print("\n❌ Failed to start JDownloader")
        sys.exit(1)
    
    # Wait for cloud connection
    print("\n⏳ Waiting 30 seconds for cloud connection to establish...")
    time.sleep(30)
    
    # Step 2: Verify connection
    if not verify_cloud_connection():
        print("\n⚠️  Connection verification failed")
        print("💡 Note: It may take 1-2 minutes for the initial connection")
        sys.exit(1)
    
    print("\n✅ All steps completed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
