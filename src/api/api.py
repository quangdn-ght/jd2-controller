#!/usr/bin/env python3
"""FastAPI RESTful API for JDownloader Authentication Management"""
import os
import time
import subprocess
import json
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from src.jdownloader.jd_auth_config import JDownloaderConfig
from src.jdownloader.jd_cloud_connector import MyJDownloaderAPI, JDownloaderService
import myjdapi

# Load environment variables
load_dotenv()


def sync_env_to_jd_config():
    """Sync .env credentials to JDownloader config file if they exist"""
    email = os.getenv("JDOWNLOADER_EMAIL")
    password = os.getenv("JDOWNLOADER_PASSWORD")
    device_name = os.getenv("JDOWNLOADER_DEVICE_NAME")
    jd_home = os.getenv("JDOWNLOADER_HOME", "/opt/jd2")
    
    if not email and not password and not device_name:
        return False
    
    config_file = Path(jd_home) / "cfg" / "org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json"
    
    if not config_file.exists():
        return False
    
    try:
        # Read existing config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Update with .env values (priority to .env)
        updated = False
        if email and config.get("email") != email:
            config["email"] = email
            updated = True
        if password and config.get("password") != password:
            config["password"] = password
            updated = True
        if device_name and config.get("devicename") != device_name:
            config["devicename"] = device_name
            updated = True
        
        # Write back if updated
        if updated:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        
        return False
    except Exception as e:
        print(f"⚠️  Warning: Could not sync .env to JDownloader config: {str(e)}")
        return False


def get_credentials():
    """Get credentials with priority: .env > JDownloader config"""
    # Priority 1: .env file
    email = os.getenv("JDOWNLOADER_EMAIL")
    password = os.getenv("JDOWNLOADER_PASSWORD")
    device_name = os.getenv("JDOWNLOADER_DEVICE_NAME")
    
    # Priority 2: JDownloader config (fallback)
    if not email or not password:
        try:
            jd_home = os.getenv("JDOWNLOADER_HOME", "/opt/jd2")
            jd = JDownloaderConfig(jd_home)
            config = jd.read_config()
            
            if not email:
                email = config.get("email")
            if not password:
                password = config.get("password")
            if not device_name:
                device_name = config.get("devicename")
        except:
            pass
    
    return email, password, device_name


class Settings(BaseSettings):
    """Application settings from environment variables"""
    jdownloader_home: str = "/opt/jd2"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="JDownloader Auth API",
    description="RESTful API for managing JDownloader MyJDownloader authentication",
    version="1.0.0"
)


# Global connection state
cloud_connection = {
    "connected": False,
    "devices": [],
    "last_check": None,
    "email": None
}


@app.on_event("startup")
async def startup_event():
    """Auto-connect to MyJDownloader cloud on startup if credentials exist"""
    print("\n" + "="*70)
    print("🚀 JDownloader Auth API Starting...".center(70))
    print("="*70)
    
    # Get credentials with priority: .env > JDownloader config
    email, password, device_name = get_credentials()
    
    # Sync .env to JDownloader config if needed
    if email or password or device_name:
        synced = sync_env_to_jd_config()
        if synced:
            print(f"🔄 Synced .env settings to JDownloader config")
    
    if email and password:
        print(f"📧 Using credentials from .env: {email}")
        if device_name:
            print(f"🏷️  Device name: {device_name}")
        print("🔌 Auto-connecting to MyJDownloader cloud...")
        
        try:
            # Try to connect using the myjdapi library
            jd_api = myjdapi.Myjdapi()
            jd_api.set_app_key("jd2controller")
            jd_api.connect(email, password)
            jd_api.update_devices()
            devices = jd_api.list_devices()
            
            # Update global connection state
            cloud_connection["connected"] = True
            cloud_connection["devices"] = devices
            cloud_connection["last_check"] = time.time()
            cloud_connection["email"] = email
            
            print(f"✅ Successfully connected to MyJDownloader cloud")
            print(f"📱 Found {len(devices)} device(s):")
            for i, device in enumerate(devices, 1):
                device_name_found = device.get("name", "Unknown")
                device_id = device.get("id", "")
                device_type = device.get("type", "")
                device_status = device.get("status", "UNKNOWN")
                print(f"   {i}. {device_name_found}")
                print(f"      ID: {device_id}")
                print(f"      Type: {device_type}")
                print(f"      Status: {device_status}")
            
            if len(devices) == 0:
                print(f"   ⚠️  No devices found. This means:")
                print(f"      • JDownloader is not running, OR")
                print(f"      • JDownloader is not connected to this MyJDownloader account")
                if device_name:
                    print(f"      • Expected device name: {device_name}")
            
        except myjdapi.exception.MYJDException as e:
            print(f"⚠️  Failed to auto-connect: {str(e)}")
            print(f"   You can still connect manually via /cloud/connect endpoint")
        except Exception as e:
            print(f"⚠️  Error during auto-connect: {str(e)}")
    else:
        print("ℹ️  No credentials found in .env or JDownloader config")
        print("   Set JDOWNLOADER_EMAIL and JDOWNLOADER_PASSWORD in .env to enable auto-connect")
    
    print("="*70 + "\n")

# API Key security (optional)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key if configured"""
    if settings.api_key:
        if not api_key or api_key != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key"
            )
    return api_key


# Pydantic models
class CredentialsUpdate(BaseModel):
    """Model for updating JDownloader credentials"""
    email: EmailStr = Field(..., description="MyJDownloader email address")
    password: str = Field(..., min_length=6, description="MyJDownloader password")
    device_name: Optional[str] = Field(None, description="Custom device name")


class ConfigResponse(BaseModel):
    """Model for configuration response"""
    email: Optional[str]
    device_name: str
    auto_connect: bool
    server_host: str


class StatusResponse(BaseModel):
    """Model for status response"""
    status: str
    message: str


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "JDownloader Headless Control API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "cli": {
                "start": "/cli/start",
                "stop": "/cli/stop",
                "restart": "/cli/restart",
                "status": "/cli/status",
                "verify": "/cli/verify",
                "logs": "/cli/logs"
            },
            "config": "/config",
            "cloud": {
                "connect": "/cloud/connect",
                "devices": "/cloud/devices",
                "verify": "/cloud/verify"
            },
            "service": {
                "status": "/service/status",
                "start": "/service/start",
                "stop": "/service/stop",
                "restart": "/service/restart"
            }
        }
    }


@app.get("/health", response_model=StatusResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return StatusResponse(
        status="healthy",
        message="JDownloader Auth API is running"
    )


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config(api_key: str = Depends(verify_api_key)):
    """Get current JDownloader configuration"""
    try:
        jd = JDownloaderConfig(settings.jdownloader_home)
        config = jd.read_config()
        
        return ConfigResponse(
            email=config.get("email"),
            device_name=config.get("devicename", "Not set"),
            auto_connect=config.get("autoconnectenabledv2", False),
            server_host=config.get("serverhost", "api.jdownloader.org")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read configuration: {str(e)}"
        )


@app.post("/config/credentials", response_model=StatusResponse, tags=["Configuration"])
async def update_credentials(
    credentials: CredentialsUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update JDownloader MyJDownloader credentials"""
    try:
        jd = JDownloaderConfig(settings.jdownloader_home)
        
        success = jd.update_credentials(
            email=credentials.email,
            password=credentials.password,
            device_name=credentials.device_name
        )
        
        if success:
            return StatusResponse(
                status="success",
                message="Credentials updated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update credentials"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating credentials: {str(e)}"
        )


@app.put("/config/credentials", response_model=StatusResponse, tags=["Configuration"])
async def put_credentials(
    credentials: CredentialsUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update JDownloader MyJDownloader credentials (PUT method)"""
    return await update_credentials(credentials, api_key)


@app.delete("/config/credentials", response_model=StatusResponse, tags=["Configuration"])
async def clear_credentials(api_key: str = Depends(verify_api_key)):
    """Clear JDownloader MyJDownloader credentials"""
    try:
        jd = JDownloaderConfig(settings.jdownloader_home)
        config = jd.read_config()
        config["email"] = None
        config["password"] = ""
        
        if jd.save_config(config):
            return StatusResponse(
                status="success",
                message="Credentials cleared successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear credentials"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing credentials: {str(e)}"
        )


@app.get("/config/status", response_model=dict, tags=["Monitoring"])
async def get_connection_status(api_key: str = Depends(verify_api_key)):
    """Get JDownloader connection status and monitoring info"""
    try:
        jd = JDownloaderConfig(settings.jdownloader_home)
        config = jd.read_config()
        
        has_credentials = bool(config.get("email") and config.get("password"))
        
        return {
            "configured": has_credentials,
            "email": config.get("email", "Not configured"),
            "device_name": config.get("devicename", "Not set"),
            "auto_connect_enabled": config.get("autoconnectenabledv2", False),
            "server_host": config.get("serverhost", "api.jdownloader.org"),
            "config_file": str(jd.config_file),
            "config_exists": jd.config_file.exists()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting status: {str(e)}"
        )


# Cloud Connection Endpoints
@app.post("/cloud/connect", response_model=dict, tags=["Cloud Connection"])
async def connect_to_cloud(api_key: str = Depends(verify_api_key)):
    """Connect to MyJDownloader cloud and verify connection"""
    try:
        # Get credentials with priority: .env > JDownloader config
        email, password, device_name = get_credentials()
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password must be configured in .env or JDownloader config"
            )
        
        # Connect to MyJDownloader API using official library
        jd_api = myjdapi.Myjdapi()
        jd_api.set_app_key("jd2controller")
        jd_api.connect(email, password)
        
        return {
            "status": "success",
            "message": "Successfully connected to MyJDownloader",
            "connected": True
        }
        
    except HTTPException:
        raise
    except myjdapi.exception.MYJDException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MyJDownloader API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to cloud: {str(e)}"
        )


@app.get("/cloud/devices", response_model=dict, tags=["Cloud Connection"])
async def list_cloud_devices(api_key: str = Depends(verify_api_key)):
    """List all devices connected to MyJDownloader cloud"""
    try:
        # Get credentials with priority: .env > JDownloader config
        email, password, device_name = get_credentials()
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password must be configured in .env or JDownloader config"
            )
        
        # Connect and list devices using official library
        jd_api = myjdapi.Myjdapi()
        jd_api.set_app_key("jd2controller")
        jd_api.connect(email, password)
        jd_api.update_devices()
        devices = jd_api.list_devices()
        
        # Update global connection state
        cloud_connection["connected"] = True
        cloud_connection["devices"] = devices
        cloud_connection["last_check"] = time.time()
        cloud_connection["email"] = email
        
        return {
            "status": "success",
            "message": f"Found {len(devices)} device(s)",
            "device_count": len(devices),
            "connected": True,
            "devices": [
                {
                    "name": d.get("name", "Unknown"),
                    "id": d.get("id", ""),
                    "type": d.get("type", ""),
                    "status": d.get("status", "UNKNOWN")
                }
                for d in devices
            ]
        }
        
    except HTTPException:
        raise
    except myjdapi.exception.MYJDException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MyJDownloader API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing devices: {str(e)}"
        )


@app.post("/cloud/verify", response_model=dict, tags=["Cloud Connection"])
async def verify_cloud_connection(api_key: str = Depends(verify_api_key)):
    """Verify that local JDownloader is connected to MyJDownloader cloud"""
    try:
        jd = JDownloaderConfig(settings.jdownloader_home)
        config = jd.read_config()
        
        email = config.get("email")
        password = config.get("password")
        device_name = config.get("devicename", "")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password must be configured first"
            )
        
        # Verify connection using official library
        jd_api = myjdapi.Myjdapi()
        jd_api.set_app_key("jd2controller")
        jd_api.connect(email, password)
        jd_api.update_devices()
        devices = jd_api.list_devices()
        
        # Check if expected device is found
        found_expected_device = False
        device_list = []
        
        for device in devices:
            device_info = {
                "name": device.get("name", "Unknown"),
                "id": device.get("id", ""),
                "type": device.get("type", ""),
                "status": device.get("status", "UNKNOWN")
            }
            device_list.append(device_info)
            
            # Check if this is the expected device
            if device_name and device.get("name", "").lower() == device_name.lower():
                found_expected_device = True
        
        connected = len(devices) > 0
        
        if not connected:
            message = "No devices found connected to MyJDownloader cloud"
        elif found_expected_device:
            message = f"Device '{device_name}' is connected"
        elif device_name:
            available_names = ", ".join([d["name"] for d in device_list])
            message = f"Device '{device_name}' not found. Available: {available_names}"
        else:
            message = f"Found {len(devices)} device(s) connected"
        
        return {
            "status": "success" if connected else "failed",
            "connected": connected,
            "message": message,
            "device_count": len(devices),
            "devices": device_list,
            "found_expected_device": found_expected_device,
            "expected_device_name": device_name
        }
        
    except HTTPException:
        raise
    except myjdapi.exception.MYJDException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MyJDownloader API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying connection: {str(e)}"
        )


# JDownloader Service Management
@app.get("/service/status", response_model=dict, tags=["Service Management"])
async def get_service_status(api_key: str = Depends(verify_api_key)):
    """Get JDownloader service status"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        status_info = service.status()
        
        return {
            "status": "success",
            **status_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting service status: {str(e)}"
        )


@app.post("/service/start", response_model=StatusResponse, tags=["Service Management"])
async def start_service(api_key: str = Depends(verify_api_key)):
    """Start JDownloader service"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        success, message = service.start()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return StatusResponse(status="success", message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting service: {str(e)}"
        )


@app.post("/service/stop", response_model=StatusResponse, tags=["Service Management"])
async def stop_service(api_key: str = Depends(verify_api_key)):
    """Stop JDownloader service"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        success, message = service.stop()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return StatusResponse(status="success", message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping service: {str(e)}"
        )


@app.post("/service/restart", response_model=StatusResponse, tags=["Service Management"])
async def restart_service(api_key: str = Depends(verify_api_key)):
    """Restart JDownloader service"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        success, message = service.restart()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return StatusResponse(status="success", message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restarting service: {str(e)}"
        )


# CLI Command Endpoints (matching jdctl functionality)
@app.post("/cli/start", response_model=dict, tags=["CLI Commands"])
async def cli_start(api_key: str = Depends(verify_api_key)):
    """Start JDownloader (like jdctl start)"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        success, message = service.start()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        # Wait a bit for JD2 to initialize
        time.sleep(3)
        
        # Get status
        status_info = service.status()
        
        return {
            "status": "success",
            "message": message,
            "running": status_info["running"],
            "pid": status_info["pid"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting JDownloader: {str(e)}"
        )


@app.post("/cli/stop", response_model=StatusResponse, tags=["CLI Commands"])
async def cli_stop(api_key: str = Depends(verify_api_key)):
    """Stop JDownloader (like jdctl stop)"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        success, message = service.stop()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return StatusResponse(status="success", message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping JDownloader: {str(e)}"
        )


@app.post("/cli/restart", response_model=dict, tags=["CLI Commands"])
async def cli_restart(api_key: str = Depends(verify_api_key)):
    """Restart JDownloader (like jdctl restart)"""
    try:
        service = JDownloaderService(settings.jdownloader_home)
        success, message = service.restart()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        # Get status after restart
        time.sleep(2)
        status_info = service.status()
        
        return {
            "status": "success",
            "message": message,
            "running": status_info["running"],
            "pid": status_info["pid"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restarting JDownloader: {str(e)}"
        )


@app.get("/cli/status", response_model=dict, tags=["CLI Commands"])
async def cli_status(api_key: str = Depends(verify_api_key)):
    """Get JDownloader status with process details (like jdctl status)"""
    try:
        # Check if running
        result = subprocess.run(
            ["/usr/bin/pgrep", "-f", "JDownloader.jar"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                "status": "stopped",
                "running": False,
                "message": "JDownloader is not running",
                "pids": [],
                "log_file": "/tmp/jd2.log"
            }
        
        pids = [pid.strip() for pid in result.stdout.strip().split('\n') if pid.strip()]
        
        # Get process details for first PID
        process_info = None
        if pids:
            ps_result = subprocess.run(
                ["/usr/bin/ps", "-p", pids[0], "-o", "pid,ppid,%cpu,%mem,etime,cmd", "--no-headers"],
                capture_output=True,
                text=True
            )
            if ps_result.returncode == 0:
                process_info = ps_result.stdout.strip()
        
        # Check log file
        log_file = Path("/tmp/jd2.log")
        log_info = None
        if log_file.exists():
            log_info = {
                "path": str(log_file),
                "size_kb": round(log_file.stat().st_size / 1024, 1),
                "exists": True
            }
        
        return {
            "status": "running",
            "running": True,
            "message": f"JDownloader is running with {len(pids)} process(es)",
            "pids": pids,
            "process_info": process_info,
            "log_file": log_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting status: {str(e)}"
        )


@app.post("/cli/verify", response_model=dict, tags=["CLI Commands"])
async def cli_verify(api_key: str = Depends(verify_api_key)):
    """Verify cloud connection with full device details (like jdctl verify)"""
    try:
        jd = JDownloaderConfig(settings.jdownloader_home)
        config = jd.read_config()
        
        email = config.get("email")
        password = config.get("password")
        device_name = config.get("devicename", "Unknown")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password must be configured first"
            )
        
        # Use official myjdapi
        jd_api = myjdapi.Myjdapi()
        jd_api.set_app_key("jd2controller")
        
        # Connect
        jd_api.connect(email, password)
        
        # Get devices
        jd_api.update_devices()
        devices = jd_api.list_devices()
        
        if not devices:
            return {
                "status": "warning",
                "connected": False,
                "message": "No devices found connected to MyJDownloader cloud",
                "email": email,
                "expected_device": device_name,
                "device_count": 0,
                "devices": []
            }
        
        # Format device list
        device_list = [
            {
                "name": d.get("name", "Unknown"),
                "id": d.get("id", "N/A"),
                "type": d.get("type", "N/A"),
                "status": d.get("status", "UNKNOWN"),
                "is_expected": (d.get("name", "").lower() == device_name.lower() or
                              device_name in d.get("name", "") or
                              d.get("name", "") in device_name)
            }
            for d in devices
        ]
        
        # Check if expected device found
        found_expected = any(d["is_expected"] for d in device_list)
        
        return {
            "status": "success",
            "connected": True,
            "message": f"Found {len(devices)} device(s) connected to cloud",
            "email": email,
            "expected_device": device_name,
            "found_expected_device": found_expected,
            "device_count": len(devices),
            "devices": device_list,
            "cloud_status": "connected",
            "web_url": "https://my.jdownloader.org"
        }
        
    except myjdapi.exception.MYJDException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MyJDownloader API Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying connection: {str(e)}"
        )


@app.get("/cli/logs", response_model=dict, tags=["CLI Commands"])
async def cli_logs(
    lines: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """Get JDownloader logs (like jdctl logs)"""
    try:
        log_file = Path("/tmp/jd2.log")
        
        if not log_file.exists():
            return {
                "status": "warning",
                "message": "Log file not found",
                "log_file": str(log_file),
                "logs": []
            }
        
        # Read last N lines
        result = subprocess.run(
            ["/usr/bin/tail", f"-{lines}", str(log_file)],
            capture_output=True,
            text=True
        )
        
        log_lines = result.stdout.strip().split('\n') if result.stdout else []
        
        return {
            "status": "success",
            "message": f"Retrieved last {len(log_lines)} lines",
            "log_file": str(log_file),
            "lines_requested": lines,
            "lines_returned": len(log_lines),
            "logs": log_lines
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading logs: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting JDownloader Auth API...")
    print(f"📍 API will be available at: http://{settings.api_host}:{settings.api_port}")
    print(f"📖 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    
    if settings.api_key:
        print("🔒 API Key authentication is ENABLED")
    else:
        print("⚠️  API Key authentication is DISABLED (set API_KEY in .env to enable)")
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=os.getenv("API_RELOAD", "false").lower() == "true"
    )
