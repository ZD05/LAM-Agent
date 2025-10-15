#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础软件集成类，提供通用的桌面软件启动和管理功能
"""

import os
import subprocess
import logging
import winreg
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseSoftwareIntegration(ABC):
    """基础软件集成类"""
    
    def __init__(self, name: str, category: str, executables: List[str], 
                 registry_paths: List[str], install_paths: List[str]):
        self.name = name
        self.category = category
        self.executables = executables
        self.registry_paths = registry_paths
        self.install_paths = install_paths
    
    def launch_software(self) -> Dict[str, Any]:
        """启动软件"""
        try:
            # 方法1: 尝试从注册表获取安装路径
            exe_path = self._get_software_exe_path()
            
            # 方法2: 尝试常见安装路径
            if not exe_path:
                exe_path = self._find_software_in_paths()
            
            # 方法3: 尝试系统PATH
            if not exe_path:
                exe_path = self._find_software_in_system_path()
            
            if not exe_path:
                return {
                    "success": False,
                    "error": f"未找到{self.name}安装路径"
                }
            
            # 启动软件
            subprocess.Popen([exe_path], shell=True)
            
            return {
                "success": True,
                "message": f"成功启动{self.name}",
                "exe_path": exe_path,
                "method": f"{self.name.lower()}_launch"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"启动{self.name}失败: {str(e)}"
            }
    
    def _get_software_exe_path(self) -> Optional[str]:
        """从注册表获取软件安装路径"""
        try:
            for registry_path in self.registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
                    install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    winreg.CloseKey(key)
                    
                    if install_path and os.path.exists(install_path):
                        for exe in self.executables:
                            exe_path = os.path.join(install_path, exe)
                            if os.path.exists(exe_path):
                                return exe_path
                except (FileNotFoundError, OSError):
                    continue
        except Exception as e:
            logger.warning(f"从注册表获取{self.name}路径失败: {e}")
        
        return None
    
    def _find_software_in_paths(self) -> Optional[str]:
        """在常见安装路径中查找软件"""
        for install_path in self.install_paths:
            if os.path.exists(install_path):
                for exe in self.executables:
                    exe_path = os.path.join(install_path, exe)
                    if os.path.exists(exe_path):
                        return exe_path
        return None
    
    def _find_software_in_system_path(self) -> Optional[str]:
        """在系统PATH中查找软件"""
        system_path = os.environ.get('PATH', '').split(os.pathsep)
        for path in system_path:
            for exe in self.executables:
                exe_path = os.path.join(path, exe)
                if os.path.exists(exe_path):
                    return exe_path
        return None
    
    @abstractmethod
    def get_special_handlers(self) -> List[str]:
        """获取特殊处理方法列表"""
        pass

class OfficeSoftwareIntegration(BaseSoftwareIntegration):
    """办公软件集成基类"""
    
    def __init__(self, name: str, executables: List[str], 
                 registry_paths: List[str], install_paths: List[str]):
        super().__init__(name, "办公软件", executables, registry_paths, install_paths)
    
    def open_document(self, file_path: str) -> Dict[str, Any]:
        """打开文档"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"文件不存在: {file_path}"
                }
            
            exe_path = self._get_software_exe_path()
            if not exe_path:
                exe_path = self._find_software_in_paths()
            
            if not exe_path:
                return {
                    "success": False,
                    "error": f"未找到{self.name}安装路径"
                }
            
            subprocess.Popen([exe_path, file_path], shell=True)
            
            return {
                "success": True,
                "message": f"使用{self.name}打开文档: {file_path}",
                "file_path": file_path,
                "method": f"{self.name.lower()}_open_document"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"打开文档失败: {str(e)}"
            }
    
    def create_document(self, file_path: str) -> Dict[str, Any]:
        """创建新文档"""
        try:
            exe_path = self._get_software_exe_path()
            if not exe_path:
                exe_path = self._find_software_in_paths()
            
            if not exe_path:
                return {
                    "success": False,
                    "error": f"未找到{self.name}安装路径"
                }
            
            subprocess.Popen([exe_path], shell=True)
            
            return {
                "success": True,
                "message": f"使用{self.name}创建新文档",
                "file_path": file_path,
                "method": f"{self.name.lower()}_create_document"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"创建文档失败: {str(e)}"
            }

class SocialSoftwareIntegration(BaseSoftwareIntegration):
    """社交软件集成基类"""
    
    def __init__(self, name: str, executables: List[str], 
                 registry_paths: List[str], install_paths: List[str]):
        super().__init__(name, "社交软件", executables, registry_paths, install_paths)
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """发送消息（需要软件支持）"""
        try:
            # 这里只是启动软件，实际的消息发送需要软件特定的API
            result = self.launch_software()
            if result["success"]:
                result["message"] = f"已启动{self.name}，请手动发送消息: {message}"
                result["method"] = f"{self.name.lower()}_send_message"
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"发送消息失败: {str(e)}"
            }
    
    def open_chat(self, contact: str) -> Dict[str, Any]:
        """打开聊天窗口（需要软件支持）"""
        try:
            # 这里只是启动软件，实际的聊天窗口打开需要软件特定的API
            result = self.launch_software()
            if result["success"]:
                result["message"] = f"已启动{self.name}，请手动打开与{contact}的聊天"
                result["method"] = f"{self.name.lower()}_open_chat"
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"打开聊天失败: {str(e)}"
            }

