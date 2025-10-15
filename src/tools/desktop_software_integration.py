#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import webbrowser
import logging
from typing import Dict, Any, List, Optional
import time
import winreg

from .base_software_integration import (
    BaseSoftwareIntegration, 
    OfficeSoftwareIntegration, 
    SocialSoftwareIntegration
)

logger = logging.getLogger(__name__)

class DesktopSoftwareIntegration:
    """桌面软件集成类，提供常用软件的启动和操作功能"""
    
    def __init__(self):
        # 常用软件配置
        self.software_configs = {
            'wps': {
                'name': 'WPS Office',
                'category': '办公软件',
                'executables': [
                    'wpsoffice.exe',
                    'wps.exe',
                    'et.exe',  # WPS表格
                    'wpp.exe',  # WPS演示
                    'wpswriter.exe'  # WPS文字
                ],
                'registry_paths': [
                    r'SOFTWARE\Kingsoft\Office',
                    r'SOFTWARE\WOW6432Node\Kingsoft\Office'
                ],
                'install_paths': [
                    'C:/Program Files (x86)/Kingsoft/WPS Office',
                    'C:/Program Files/Kingsoft/WPS Office',
                    'D:/Program Files (x86)/Kingsoft/WPS Office',
                    'D:/Program Files/Kingsoft/WPS Office'
                ],
                'special_handlers': ['wps_open_document', 'wps_create_document']
            },
            'wechat': {
                'name': '微信',
                'category': '社交软件',
                'executables': [
                    'WeChat.exe',
                    'wechat.exe'
                ],
                'registry_paths': [
                    r'SOFTWARE\Tencent\WeChat',
                    r'SOFTWARE\WOW6432Node\Tencent\WeChat'
                ],
                'install_paths': [
                    'C:/Program Files (x86)/Tencent/WeChat',
                    'C:/Program Files/Tencent/WeChat',
                    'D:/Program Files (x86)/Tencent/WeChat',
                    'D:/Program Files/Tencent/WeChat'
                ],
                'special_handlers': ['wechat_send_message', 'wechat_open_chat']
            },
            'qq': {
                'name': 'QQ',
                'category': '社交软件',
                'executables': [
                    'QQ.exe',
                    'qq.exe',
                    'QQProtect.exe'
                ],
                'registry_paths': [
                    r'SOFTWARE\Tencent\QQ',
                    r'SOFTWARE\WOW6432Node\Tencent\QQ'
                ],
                'install_paths': [
                    'C:/Program Files (x86)/Tencent/QQ',
                    'C:/Program Files/Tencent/QQ',
                    'D:/Program Files (x86)/Tencent/QQ',
                    'D:/Program Files/Tencent/QQ'
                ],
                'special_handlers': ['qq_send_message', 'qq_open_chat']
            }
        }
    
    def launch_software(self, software_name: str) -> Dict[str, Any]:
        """启动桌面软件"""
        try:
            software_name = software_name.lower()
            if software_name not in self.software_configs:
                return {
                    "success": False,
                    "error": f"不支持的软件: {software_name}"
                }
            
            config = self.software_configs[software_name]
            
            # 方法1: 尝试从注册表获取安装路径
            exe_path = self._get_software_exe_path(software_name)
            
            # 方法2: 尝试常见安装路径
            if not exe_path:
                exe_path = self._find_software_in_paths(config['install_paths'], config['executables'])
            
            # 方法3: 尝试桌面快捷方式
            if not exe_path:
                shortcut_path = self._find_desktop_shortcut(config['name'])
                if shortcut_path:
                    try:
                        subprocess.run(["start", "", shortcut_path], shell=True, check=True, timeout=5)
                        return {
                            "success": True,
                            "message": f"通过桌面快捷方式启动{config['name']}",
                            "software": config['name'],
                            "method": "desktop_shortcut"
                        }
                    except subprocess.CalledProcessError:
                        pass
            
            # 方法4: 尝试启动可执行文件
            if exe_path:
                try:
                    subprocess.Popen([exe_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {
                        "success": True,
                        "message": f"启动{config['name']}成功",
                        "software": config['name'],
                        "exe_path": exe_path,
                        "method": "executable"
                    }
                except Exception as e:
                    logger.warning(f"启动{config['name']}失败: {e}")
            
            # 方法5: 尝试通过start命令启动
            for exe_name in config['executables']:
                try:
                    subprocess.run(["start", "", exe_name], shell=True, check=True, timeout=5)
                    return {
                        "success": True,
                        "message": f"通过start命令启动{config['name']}",
                        "software": config['name'],
                        "executable": exe_name,
                        "method": "start_command"
                    }
                except subprocess.CalledProcessError:
                    continue
            
            return {
                "success": False,
                "error": f"无法启动{config['name']}，请检查是否已安装"
            }
            
        except Exception as e:
            logger.error(f"启动软件失败: {e}")
            return {
                "success": False,
                "error": f"启动软件失败: {str(e)}"
            }
    
    def get_software_info(self, software_name: str) -> Dict[str, Any]:
        """获取软件信息"""
        try:
            software_name = software_name.lower()
            if software_name not in self.software_configs:
                return {
                    "success": False,
                    "error": f"不支持的软件: {software_name}"
                }
            
            config = self.software_configs[software_name]
            
            # 检查软件是否已安装
            exe_path = self._get_software_exe_path(software_name)
            if not exe_path:
                exe_path = self._find_software_in_paths(config['install_paths'], config['executables'])
            
            shortcut_path = self._find_desktop_shortcut(config['name'])
            
            return {
                "success": True,
                "software": config['name'],
                "category": config['category'],
                "executables": config['executables'],
                "install_paths": config['install_paths'],
                "special_handlers": config['special_handlers'],
                "exe_path": exe_path,
                "shortcut_path": shortcut_path,
                "is_installed": bool(exe_path or shortcut_path)
            }
            
        except Exception as e:
            logger.error(f"获取软件信息失败: {e}")
            return {
                "success": False,
                "error": f"获取软件信息失败: {str(e)}"
            }
    
    def list_available_software(self) -> Dict[str, Any]:
        """列出所有可用的软件"""
        try:
            available_software = []
            
            for software_name, config in self.software_configs.items():
                exe_path = self._get_software_exe_path(software_name)
                if not exe_path:
                    exe_path = self._find_software_in_paths(config['install_paths'], config['executables'])
                
                shortcut_path = self._find_desktop_shortcut(config['name'])
                
                available_software.append({
                    "name": config['name'],
                    "category": config['category'],
                    "is_installed": bool(exe_path or shortcut_path),
                    "exe_path": exe_path,
                    "shortcut_path": shortcut_path
                })
            
            return {
                "success": True,
                "software_list": available_software,
                "total_count": len(available_software),
                "installed_count": sum(1 for s in available_software if s['is_installed'])
            }
            
        except Exception as e:
            logger.error(f"列出软件失败: {e}")
            return {
                "success": False,
                "error": f"列出软件失败: {str(e)}"
            }
    
    def _get_software_exe_path(self, software_name: str) -> Optional[str]:
        """从注册表获取软件可执行文件路径"""
        try:
            config = self.software_configs[software_name]
            
            for reg_path in config['registry_paths']:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    winreg.CloseKey(key)
                    
                    # 查找可执行文件
                    for exe_name in config['executables']:
                        exe_path = os.path.join(install_path, exe_name)
                        if os.path.exists(exe_path):
                            return exe_path
                            
                except (FileNotFoundError, OSError):
                    continue
                    
        except Exception as e:
            logger.warning(f"从注册表获取{software_name}路径失败: {e}")
        
        return None
    
    def _find_software_in_paths(self, install_paths: List[str], executables: List[str]) -> Optional[str]:
        """在指定路径中查找软件"""
        for install_path in install_paths:
            if os.path.exists(install_path):
                for exe_name in executables:
                    exe_path = os.path.join(install_path, exe_name)
                    if os.path.exists(exe_path):
                        return exe_path
        return None
    
    def _find_desktop_shortcut(self, software_name: str) -> Optional[str]:
        """查找桌面快捷方式"""
        desktop_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/桌面")
        ]
        
        for desktop_path in desktop_paths:
            if os.path.exists(desktop_path):
                for file in os.listdir(desktop_path):
                    if file.endswith('.lnk') and software_name.lower() in file.lower():
                        return os.path.join(desktop_path, file)
        return None

# WPS Office专用处理
class WPSIntegration(OfficeSoftwareIntegration):
    """WPS Office专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="WPS Office",
            executables=[
                'wpsoffice.exe',
                'wps.exe',
                'et.exe',  # WPS表格
                'wpp.exe',  # WPS演示
                'wpswriter.exe'  # WPS文字
            ],
            registry_paths=[
                r'SOFTWARE\Kingsoft\Office',
                r'SOFTWARE\WOW6432Node\Kingsoft\Office'
            ],
            install_paths=[
                'C:/Program Files (x86)/Kingsoft/WPS Office',
                'C:/Program Files/Kingsoft/WPS Office',
                'D:/Program Files (x86)/Kingsoft/WPS Office',
                'D:/Program Files/Kingsoft/WPS Office'
            ]
        )
    
    def get_special_handlers(self) -> List[str]:
        """获取特殊处理方法列表"""
        return ['wps_open_document', 'wps_create_document']
    
    def create_document(self, doc_type: str = "writer") -> Dict[str, Any]:
        """创建WPS文档"""
        try:
            # WPS文档类型映射
            doc_types = {
                "writer": "wpswriter.exe",
                "et": "et.exe",
                "wpp": "wpp.exe"
            }
            
            if doc_type not in doc_types:
                return {
                    "success": False,
                    "error": f"不支持的文档类型: {doc_type}"
                }
            
            exe_name = doc_types[doc_type]
            
            # 尝试启动对应的WPS组件
            subprocess.Popen([exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return {
                "success": True,
                "message": f"创建WPS{doc_type}文档",
                "doc_type": doc_type,
                "executable": exe_name,
                "method": "create_document"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"创建WPS文档失败: {str(e)}"
            }

# 微信专用处理
class WeChatIntegration(SocialSoftwareIntegration):
    """微信专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="微信",
            executables=[
                'WeChat.exe',
                'wechat.exe'
            ],
            registry_paths=[
                r'SOFTWARE\Tencent\WeChat',
                r'SOFTWARE\WOW6432Node\Tencent\WeChat'
            ],
            install_paths=[
                'C:/Program Files (x86)/Tencent/WeChat',
                'C:/Program Files/Tencent/WeChat',
                'D:/Program Files (x86)/Tencent/WeChat',
                'D:/Program Files/Tencent/WeChat'
            ]
        )
    
    def get_special_handlers(self) -> List[str]:
        """获取特殊处理方法列表"""
        return ['wechat_send_message', 'wechat_open_chat']
    
    def send_message(self, contact: str = "", message: str = "") -> Dict[str, Any]:
        """发送微信消息（模拟）"""
        try:
            # 启动微信
            launch_result = self.launch_software()
            
            if not launch_result.get('success'):
                return launch_result
            
            # 模拟发送消息（实际需要微信API或自动化工具）
            return {
                "success": True,
                "message": f"微信已启动，请手动发送消息给 {contact}: {message}",
                "contact": contact,
                "message": message,
                "method": "manual_send"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"发送微信消息失败: {str(e)}"
            }
    
    def open_chat(self, contact: str = "") -> Dict[str, Any]:
        """打开微信聊天窗口"""
        try:
            # 启动微信
            launch_result = self.launch_software()
            
            if not launch_result.get('success'):
                return launch_result
            
            return {
                "success": True,
                "message": f"微信已启动，请手动打开与 {contact} 的聊天窗口",
                "contact": contact,
                "method": "manual_open"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"打开微信聊天失败: {str(e)}"
            }

# QQ专用处理
class QQIntegration(SocialSoftwareIntegration):
    """QQ专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="QQ",
            executables=[
                'QQ.exe',
                'qq.exe',
                'QQProtect.exe'
            ],
            registry_paths=[
                r'SOFTWARE\Tencent\QQ',
                r'SOFTWARE\WOW6432Node\Tencent\QQ'
            ],
            install_paths=[
                'C:/Program Files (x86)/Tencent/QQ',
                'C:/Program Files/Tencent/QQ',
                'D:/Program Files (x86)/Tencent/QQ',
                'D:/Program Files/Tencent/QQ'
            ]
        )
    
    def get_special_handlers(self) -> List[str]:
        """获取特殊处理方法列表"""
        return ['qq_send_message', 'qq_open_chat']
    
    def send_message(self, contact: str = "", message: str = "") -> Dict[str, Any]:
        """发送QQ消息（模拟）"""
        try:
            # 启动QQ
            launch_result = self.launch_software()
            
            if not launch_result.get('success'):
                return launch_result
            
            # 模拟发送消息（实际需要QQAPI或自动化工具）
            return {
                "success": True,
                "message": f"QQ已启动，请手动发送消息给 {contact}: {message}",
                "contact": contact,
                "message": message,
                "method": "manual_send"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"发送QQ消息失败: {str(e)}"
            }
    
    def open_chat(self, contact: str = "") -> Dict[str, Any]:
        """打开QQ聊天窗口"""
        try:
            # 启动QQ
            launch_result = self.launch_software()
            
            if not launch_result.get('success'):
                return launch_result
            
            return {
                "success": True,
                "message": f"QQ已启动，请手动打开与 {contact} 的聊天窗口",
                "contact": contact,
                "method": "manual_open"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"打开QQ聊天失败: {str(e)}"
            }

# 全局实例
desktop_software_integration = DesktopSoftwareIntegration()
wps_integration = WPSIntegration()
wechat_integration = WeChatIntegration()
qq_integration = QQIntegration()


