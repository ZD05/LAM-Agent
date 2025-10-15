#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桌面工具处理器
"""

import logging
from typing import Dict, Any
from ..core.base import BaseToolHandler

logger = logging.getLogger(__name__)

class DesktopScanHandler(BaseToolHandler):
    """桌面扫描处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理桌面扫描"""
        file_type = args.get("file_type", "all")
        
        try:
            from src.tools.desktop_launcher import DesktopLauncher
            launcher = DesktopLauncher()
            result = launcher.scan_desktop_files(file_type)
            return result
        except Exception as e:
            logger.error(f"桌面扫描失败: {e}")
            return {"error": f"桌面扫描失败: {str(e)}"}

class DesktopLaunchHandler(BaseToolHandler):
    """桌面启动处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理桌面启动"""
        file_name = args["file_name"]
        
        try:
            from src.tools.desktop_launcher import DesktopLauncher
            launcher = DesktopLauncher()
            result = launcher.launch_file(file_name)
            return result
        except Exception as e:
            logger.error(f"桌面启动失败: {e}")
            return {"error": f"桌面启动失败: {str(e)}"}

class DesktopSoftwareHandler(BaseToolHandler):
    """桌面软件处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理桌面软件操作"""
        action = args["action"]
        
        try:
            from src.tools.desktop_software_integration import DesktopSoftwareIntegration
            software_integration = DesktopSoftwareIntegration()
            
            if action == "launch_software":
                software_name = args["software_name"]
                result = software_integration.launch_software(software_name)
            elif action == "get_software_info":
                software_name = args["software_name"]
                result = software_integration.get_software_info(software_name)
            elif action == "list_available_software":
                result = software_integration.list_available_software()
            elif action == "wps_open_document":
                document_path = args["document_path"]
                result = software_integration.wps_open_document(document_path)
            elif action == "wps_create_document":
                document_name = args["document_name"]
                result = software_integration.wps_create_document(document_name)
            elif action == "wechat_send_message":
                contact = args["contact"]
                message = args["message"]
                result = software_integration.wechat_send_message(contact, message)
            elif action == "wechat_open_chat":
                contact = args["contact"]
                result = software_integration.wechat_open_chat(contact)
            elif action == "qq_send_message":
                contact = args["contact"]
                message = args["message"]
                result = software_integration.qq_send_message(contact, message)
            elif action == "qq_open_chat":
                contact = args["contact"]
                result = software_integration.qq_open_chat(contact)
            else:
                return {"error": f"不支持的操作: {action}"}
            
            return result
        except Exception as e:
            logger.error(f"桌面软件操作失败: {e}")
            return {"error": f"桌面软件操作失败: {str(e)}"}


