#!/usr/bin/env python3
"""JDownloader Cloud Authentication Configuration Script"""
import json, os, sys, argparse, socket
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JDownloaderConfig:
    def __init__(self, jd_home: str = None):
        if jd_home is None:
            jd_home = os.getenv("JDOWNLOADER_HOME", "/opt/jd2")
        self.jd_home = Path(jd_home)
        self.config_dir = self.jd_home / "cfg"
        self.config_file = self.config_dir / "org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json"
    
    def read_config(self) -> Dict:
        if not self.config_file.exists():
            return self._get_default_config()
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        return {
            "autoconnectenabledv2": True,
            "password": "",
            "devicename": f"JDownloader@{socket.gethostname()}",
            "email": None,
            "serverhost": "api.jdownloader.org"
        }
    
    def update_credentials(self, email: str, password: str, device_name: Optional[str] = None) -> bool:
        config = self.read_config()
        if not email or "@" not in email:
            print(f"✗ Invalid email: {email}")
            return False
        if not password or len(password) < 6:
            print(f"✗ Password too short")
            return False
        config["email"] = email
        config["password"] = password
        config["autoconnectenabledv2"] = True
        if device_name:
            config["devicename"] = device_name
        return self.save_config(config)
    
    def save_config(self, config: Dict) -> bool:
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            print(f"✓ Configuration saved")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def display_config(self) -> None:
        config = self.read_config()
        print("\n" + "="*60)
        print("MyJDownloader Configuration")
        print("="*60)
        print(f"Email:        {config.get('email', 'Not set')}")
        print(f"Device:       {config.get('devicename', 'Not set')}")
        print(f"Auto Connect: {config.get('autoconnectenabledv2', False)}")
        print(f"Server:       {config.get('serverhost', 'N/A')}")
        print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure JDownloader MyJDownloader")
    parser.add_argument("--email", "-e", help="Email address (or use JDOWNLOADER_EMAIL env var)")
    parser.add_argument("--password", "-p", help="Password (or use JDOWNLOADER_PASSWORD env var)")
    parser.add_argument("--device-name", "-d", help="Device name (or use JDOWNLOADER_DEVICE_NAME env var)")
    parser.add_argument("--show-config", action="store_true", help="Show config")
    args = parser.parse_args()
    
    jd = JDownloaderConfig()
    
    # Get credentials from args or environment variables
    email = args.email or os.getenv("JDOWNLOADER_EMAIL")
    password = args.password or os.getenv("JDOWNLOADER_PASSWORD")
    device_name = args.device_name or os.getenv("JDOWNLOADER_DEVICE_NAME")
    
    if args.show_config:
        jd.display_config()
    elif email and password:
        if jd.update_credentials(email, password, device_name):
            print("✓ Credentials configured!")
    else:
        jd.display_config()
