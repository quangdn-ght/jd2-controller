#!/usr/bin/env python3
"""WebSocket Controller for JDownloader using myjdapi"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import myjdapi
from dotenv import load_dotenv
from src.jdownloader.jd_auth_config import JDownloaderConfig

load_dotenv()


class JDownloaderWebSocketController:
    """
    WebSocket controller for JDownloader operations through MyJDownloader cloud.
    Provides real-time control and monitoring of downloads.
    """
    
    def __init__(self):
        self.jd_api = None
        self.device = None
        self.email = None
        self.password = None
        self.connected = False
        self.monitoring = False
        
    async def connect(self) -> Dict[str, Any]:
        """
        Connect to MyJDownloader cloud and get the device.
        Returns connection status and details.
        """
        try:
            # Get credentials from config
            jd_config = JDownloaderConfig()
            config = jd_config.read_config()
            
            self.email = config.get("email")
            self.password = config.get("password")
            device_name = config.get("devicename", "JDownloader@root")
            
            if not self.email or not self.password:
                return {
                    "success": False,
                    "error": "No credentials configured"
                }
            
            # Create API client
            self.jd_api = myjdapi.Myjdapi()
            self.jd_api.set_app_key("jd2controller")
            
            # Connect to cloud
            self.jd_api.connect(self.email, self.password)
            
            # Update and get devices
            self.jd_api.update_devices()
            devices = self.jd_api.list_devices()
            
            if not devices:
                return {
                    "success": False,
                    "error": "No devices found"
                }
            
            # Get device info from list
            device_info = devices[0]
            device_name = device_info.get('name', 'unknown')
            device_id = device_info.get('id', 'unknown')
            device_type = device_info.get('type', 'unknown')
            
            # Get the actual device object using get_device
            # The device object has linkgrabber, downloads, downloadcontroller attributes
            self.device = self.jd_api.get_device(device_name, device_id)
            self.connected = True
            
            return {
                "success": True,
                "device_name": device_name,
                "device_id": device_id,
                "device_type": device_type,
                "status": "connected"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def disconnect(self) -> Dict[str, Any]:
        """Disconnect from MyJDownloader"""
        try:
            if self.jd_api:
                self.jd_api.disconnect()
            self.connected = False
            self.device = None
            return {
                "success": True,
                "status": "disconnected"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_links(self, links: List[str], package_name: str = None) -> Dict[str, Any]:
        """
        Add download links to JDownloader.
        
        Args:
            links: List of URLs to download
            package_name: Optional package name for organizing downloads
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            # Get linkgrabber device
            linkgrabber = self.device.linkgrabber
            
            # Add links
            result = linkgrabber.add_links([{
                "autostart": False,
                "links": "\n".join(links),
                "packageName": package_name or f"Package_{int(time.time())}",
                "extractPassword": None,
                "priority": "DEFAULT",
                "downloadPassword": None,
                "destinationFolder": None
            }])
            
            return {
                "success": True,
                "links_added": len(links),
                "package_name": package_name,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_downloads(self) -> Dict[str, Any]:
        """
        Get all current downloads with their status.
        
        Returns:
            List of downloads with detailed information
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            downloads = self.device.downloads
            
            # Get download links
            links = downloads.query_links()
            
            # Get packages
            packages = downloads.query_packages()
            
            download_info = []
            for link in links:
                download_info.append({
                    "name": link.get("name", "Unknown"),
                    "status": link.get("status", "Unknown"),
                    "bytesTotal": link.get("bytesTotal", 0),
                    "bytesLoaded": link.get("bytesLoaded", 0),
                    "speed": link.get("speed", 0),
                    "eta": link.get("eta", 0),
                    "enabled": link.get("enabled", True),
                    "finished": link.get("finished", False),
                    "uuid": link.get("uuid", ""),
                    "url": link.get("url", "")
                })
            
            return {
                "success": True,
                "downloads": download_info,
                "packages": packages,
                "total_downloads": len(download_info)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_linkgrabber(self) -> Dict[str, Any]:
        """
        Get links in the linkgrabber (not yet added to downloads).
        
        Returns:
            List of links in linkgrabber
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            linkgrabber = self.device.linkgrabber
            
            # Get links from linkgrabber
            links = linkgrabber.query_links()
            packages = linkgrabber.query_packages()
            
            linkgrabber_info = []
            for link in links:
                linkgrabber_info.append({
                    "name": link.get("name", "Unknown"),
                    "url": link.get("url", ""),
                    "bytesTotal": link.get("bytesTotal", 0),
                    "enabled": link.get("enabled", True),
                    "uuid": link.get("uuid", ""),
                    "packageUUID": link.get("packageUUID", "")
                })
            
            return {
                "success": True,
                "linkgrabber": linkgrabber_info,
                "packages": packages,
                "total_links": len(linkgrabber_info)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_downloads(self, link_ids: List[int] = None) -> Dict[str, Any]:
        """
        Start downloads. If link_ids provided, start specific downloads.
        Otherwise, start all downloads.
        
        Args:
            link_ids: Optional list of link IDs to start
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            downloads = self.device.downloads
            
            if link_ids:
                # Start specific downloads
                downloads.resume_links(link_ids)
                message = f"Started {len(link_ids)} downloads"
            else:
                # Start all downloads
                result = self.device.downloadcontroller.start()
                message = "Started all downloads"
            
            return {
                "success": True,
                "message": message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def pause_downloads(self, link_ids: List[int] = None) -> Dict[str, Any]:
        """
        Pause downloads. If link_ids provided, pause specific downloads.
        Otherwise, pause all downloads.
        
        Args:
            link_ids: Optional list of link IDs to pause
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            downloads = self.device.downloads
            
            if link_ids:
                # Pause specific downloads (by disabling)
                downloads.set_enabled(False, link_ids)
                message = f"Paused {len(link_ids)} downloads"
            else:
                # Pause all downloads
                result = self.device.downloadcontroller.pause()
                message = "Paused all downloads"
            
            return {
                "success": True,
                "message": message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_downloads(self) -> Dict[str, Any]:
        """
        Stop all downloads completely.
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            result = self.device.downloadcontroller.stop()
            
            return {
                "success": True,
                "message": "Stopped all downloads"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def remove_links(self, link_ids: List[int], package_ids: List[int] = None) -> Dict[str, Any]:
        """
        Remove links from downloads.
        
        Args:
            link_ids: List of link IDs to remove
            package_ids: Optional list of package IDs to remove
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            downloads = self.device.downloads
            
            # Remove links
            if link_ids:
                downloads.remove_links(link_ids)
            
            # Remove packages if specified
            if package_ids:
                downloads.remove_packages(package_ids)
            
            return {
                "success": True,
                "removed_links": len(link_ids) if link_ids else 0,
                "removed_packages": len(package_ids) if package_ids else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def move_to_downloads(self, link_ids: List[int] = None, package_ids: List[int] = None) -> Dict[str, Any]:
        """
        Move links from linkgrabber to downloads.
        
        Args:
            link_ids: Optional list of link IDs to move
            package_ids: Optional list of package IDs to move
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            linkgrabber = self.device.linkgrabber
            
            # Move links to downloads
            if link_ids:
                linkgrabber.move_to_downloadlist(link_ids, [])
            
            # Move packages to downloads
            if package_ids:
                linkgrabber.move_to_downloadlist([], package_ids)
            
            return {
                "success": True,
                "moved_links": len(link_ids) if link_ids else 0,
                "moved_packages": len(package_ids) if package_ids else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_download_status(self) -> Dict[str, Any]:
        """
        Get overall download status and statistics.
        
        Returns:
            Download statistics and status
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            # Get download controller status
            status = self.device.downloadcontroller.get_current_state()
            
            # Get downloads info
            downloads_info = await self.get_downloads()
            
            # Calculate statistics
            total_bytes = 0
            loaded_bytes = 0
            active_downloads = 0
            
            if downloads_info.get("success"):
                for download in downloads_info.get("downloads", []):
                    total_bytes += download.get("bytesTotal", 0)
                    loaded_bytes += download.get("bytesLoaded", 0)
                    if download.get("status") == "Downloading":
                        active_downloads += 1
            
            progress = (loaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
            
            return {
                "success": True,
                "state": status,
                "active_downloads": active_downloads,
                "total_downloads": downloads_info.get("total_downloads", 0),
                "total_bytes": total_bytes,
                "loaded_bytes": loaded_bytes,
                "progress": round(progress, 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup_linkgrabber(self, link_ids: List[int] = None, package_ids: List[int] = None, 
                                 mode: str = "ALL", action: str = "REMOVE_LINKS") -> Dict[str, Any]:
        """
        Clean up linkgrabber by removing links/packages.
        
        Args:
            link_ids: Optional list of link IDs to clean
            package_ids: Optional list of package IDs to clean
            mode: Cleanup mode (ALL, SELECTED, etc.)
            action: Action to perform (REMOVE_LINKS, etc.)
        
        Returns:
            Status of the operation
        """
        if not self.connected or not self.device:
            return {"success": False, "error": "Not connected"}
        
        try:
            linkgrabber = self.device.linkgrabber
            
            # Remove from linkgrabber
            if link_ids:
                linkgrabber.remove_links(link_ids)
            
            if package_ids:
                linkgrabber.remove_packages(package_ids)
            
            return {
                "success": True,
                "message": "Linkgrabber cleaned"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
