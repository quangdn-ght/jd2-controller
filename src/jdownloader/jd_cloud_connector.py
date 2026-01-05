#!/usr/bin/env python3
"""MyJDownloader Cloud Connection and Verification Module"""
import hashlib
import hmac
import time
import json
import requests
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class MyJDownloaderAPI:
    """Client for MyJDownloader API"""
    
    API_URL = "https://api.jdownloader.org"
    APP_KEY = "http://git.io/vmcsk"  # Standard MyJDownloader app key
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session_token = None
        self.regain_token = None
        self.device_id = None
        self.device_secret = None
        
    def _create_secret(self, username: str, password: str, domain: str) -> bytes:
        """Create login secret"""
        secret_hash = hashlib.sha256()
        secret_hash.update(username.lower().encode('utf-8'))
        secret_hash.update(password.encode('utf-8'))
        secret_hash.update(domain.lower().encode('utf-8'))
        return secret_hash.digest()
    
    def _sign_request(self, key: bytes, data: str) -> str:
        """Sign request with HMAC-SHA256"""
        signature = hmac.new(key, data.encode('utf-8'), hashlib.sha256)
        return signature.hexdigest()
    
    def _create_query_string(self, params: Dict) -> str:
        """Create query string from parameters"""
        return '&'.join([f"{k}={v}" for k, v in params.items()])
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to MyJDownloader and get session token"""
        try:
            # Create login secret
            login_secret = self._create_secret(self.email, self.password, "server")
            
            # Create query parameters
            query_params = {
                "email": self.email,
                "appkey": self.APP_KEY
            }
            
            # Create signature
            query_string = self._create_query_string(query_params)
            signature = self._sign_request(login_secret, query_string)
            query_params["signature"] = signature
            
            # Make connect request with proper headers
            headers = {
                'User-Agent': 'JDownloader',
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.get(
                f"{self.API_URL}/my/connect",
                params=query_params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return False, f"Connection failed with status {response.status_code}: {response.text}"
            
            data = response.json()
            
            self.session_token = data.get("sessiontoken")
            self.regain_token = data.get("regaintoken")
            
            if not self.session_token:
                return False, "No session token received"
            
            return True, "Successfully connected to MyJDownloader"
            
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def list_devices(self) -> Tuple[bool, List[Dict], str]:
        """List all connected devices"""
        if not self.session_token:
            success, message = self.connect()
            if not success:
                return False, [], message
        
        try:
            # Create request ID (timestamp)
            rid = str(int(time.time() * 1000))
            
            # Create login secret for signature
            login_secret = self._create_secret(self.email, self.password, "server")
            
            # Create query parameters
            query_params = {
                "sessiontoken": self.session_token,
                "rid": rid
            }
            
            # Create signature
            query_string = self._create_query_string(query_params)
            signature = self._sign_request(login_secret, query_string)
            query_params["signature"] = signature
            
            # Make request
            response = requests.post(
                f"{self.API_URL}/my/listdevices",
                params=query_params,
                timeout=10
            )
            
            if response.status_code != 200:
                return False, [], f"List devices failed with status {response.status_code}"
            
            data = response.json()
            devices = data.get("list", [])
            
            return True, devices, f"Found {len(devices)} device(s)"
            
        except Exception as e:
            return False, [], f"Error listing devices: {str(e)}"
    
    def find_device(self, device_name: str = None) -> Tuple[bool, Optional[Dict], str]:
        """Find a specific device by name"""
        success, devices, message = self.list_devices()
        
        if not success:
            return False, None, message
        
        if not devices:
            return False, None, "No devices found"
        
        # If no device name specified, return first device
        if not device_name:
            return True, devices[0], f"Found device: {devices[0].get('name', 'Unknown')}"
        
        # Search for device by name
        for device in devices:
            if device.get("name", "").lower() == device_name.lower():
                return True, device, f"Found device: {device.get('name')}"
        
        return False, None, f"Device '{device_name}' not found"
    
    def verify_connection(self, expected_device_name: str = None) -> Tuple[bool, Dict]:
        """Verify JDownloader is connected to MyJDownloader cloud"""
        success, devices, message = self.list_devices()
        
        result = {
            "connected": success,
            "message": message,
            "devices": [],
            "device_count": 0,
            "found_expected_device": False
        }
        
        if success:
            result["devices"] = [
                {
                    "name": d.get("name", "Unknown"),
                    "id": d.get("id", ""),
                    "type": d.get("type", ""),
                    "status": d.get("status", "OFFLINE")
                }
                for d in devices
            ]
            result["device_count"] = len(devices)
            
            # Check if expected device is in the list
            if expected_device_name:
                for device in devices:
                    if device.get("name", "").lower() == expected_device_name.lower():
                        result["found_expected_device"] = True
                        result["message"] = f"Device '{expected_device_name}' is connected"
                        break
                
                if not result["found_expected_device"]:
                    result["message"] = f"Device '{expected_device_name}' not found. Available: {', '.join([d.get('name', 'Unknown') for d in devices])}"
        
        return success, result


class JDownloaderService:
    """Manage JDownloader service"""
    
    def __init__(self, jd_home: str = "/opt/jd2"):
        self.jd_home = Path(jd_home)
        self.jar_file = self.jd_home / "JDownloader.jar"
    
    def is_running(self) -> Tuple[bool, int]:
        """Check if JDownloader is running"""
        try:
            result = subprocess.run(
                ["/usr/bin/pgrep", "-f", "JDownloader.jar"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pid = int(result.stdout.strip().split()[0])
                return True, pid
            return False, 0
            
        except Exception:
            return False, 0
    
    def start(self) -> Tuple[bool, str]:
        """Start JDownloader service"""
        is_running, pid = self.is_running()
        
        if is_running:
            return True, f"JDownloader is already running (PID: {pid})"
        
        if not self.jar_file.exists():
            return False, f"JDownloader.jar not found at {self.jar_file}"
        
        try:
            # Start JDownloader in background
            subprocess.Popen(
                ["/usr/bin/java", "-Djava.awt.headless=true", "-jar", str(self.jar_file), "-norestart"],
                cwd=str(self.jd_home),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Wait a bit and verify
            time.sleep(2)
            is_running, pid = self.is_running()
            
            if is_running:
                return True, f"JDownloader started successfully (PID: {pid})"
            else:
                return False, "JDownloader failed to start"
                
        except Exception as e:
            return False, f"Error starting JDownloader: {str(e)}"
    
    def stop(self) -> Tuple[bool, str]:
        """Stop JDownloader service"""
        is_running, pid = self.is_running()
        
        if not is_running:
            return True, "JDownloader is not running"
        
        try:
            subprocess.run(["/usr/bin/kill", str(pid)], check=True)
            time.sleep(1)
            
            # Verify stopped
            is_running, _ = self.is_running()
            if not is_running:
                return True, f"JDownloader stopped (PID: {pid})"
            else:
                # Force kill if still running
                subprocess.run(["/usr/bin/kill", "-9", str(pid)], check=True)
                return True, f"JDownloader force stopped (PID: {pid})"
                
        except Exception as e:
            return False, f"Error stopping JDownloader: {str(e)}"
    
    def restart(self) -> Tuple[bool, str]:
        """Restart JDownloader service"""
        # Stop
        success, stop_msg = self.stop()
        if not success and "not running" not in stop_msg:
            return False, f"Failed to stop: {stop_msg}"
        
        # Wait a bit
        time.sleep(2)
        
        # Start
        success, start_msg = self.start()
        return success, f"Restart: {stop_msg} -> {start_msg}"
    
    def status(self) -> Dict:
        """Get JDownloader service status"""
        is_running, pid = self.is_running()
        
        return {
            "running": is_running,
            "pid": pid if is_running else None,
            "jar_path": str(self.jar_file),
            "jar_exists": self.jar_file.exists()
        }


def test_connection(email: str, password: str, device_name: str = None) -> None:
    """Test connection to MyJDownloader"""
    print("="*60)
    print("MyJDownloader Connection Test")
    print("="*60)
    
    api = MyJDownloaderAPI(email, password)
    
    print(f"\n📧 Email: {email}")
    print("🔑 Connecting to MyJDownloader...")
    
    success, message = api.connect()
    print(f"{'✅' if success else '❌'} {message}")
    
    if success:
        print(f"🎟️  Session Token: {api.session_token[:20]}...")
        
        print("\n📱 Listing devices...")
        success, devices, message = api.list_devices()
        print(f"{'✅' if success else '❌'} {message}")
        
        if success and devices:
            print("\n🔍 Connected Devices:")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device.get('name', 'Unknown')}")
                print(f"     ID: {device.get('id', 'N/A')}")
                print(f"     Type: {device.get('type', 'N/A')}")
                print(f"     Status: {device.get('status', 'OFFLINE')}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    email = os.getenv("JDOWNLOADER_EMAIL")
    password = os.getenv("JDOWNLOADER_PASSWORD")
    device_name = os.getenv("JDOWNLOADER_DEVICE_NAME")
    
    if not email or not password:
        print("❌ Error: JDOWNLOADER_EMAIL and JDOWNLOADER_PASSWORD must be set in .env file")
        exit(1)
    
    test_connection(email, password, device_name)
