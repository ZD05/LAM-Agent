#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import win32com.client
import win32api
import win32con

logger = logging.getLogger(__name__)


class SafeDesktopLauncher:
    """安全桌面启动器类，避免黑屏问题"""
    
    def __init__(self):
        self.desktop_path = self._get_desktop_path()
        self.supported_extensions = {
            '.exe', '.bat', '.cmd', '.lnk', '.url', '.py', '.pyw',
            '.msi', '.appx', '.appxbundle'
        }
    
    def _get_desktop_path(self) -> str:
        """获取桌面路径"""
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if os.path.exists(desktop):
                return desktop
            
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            desktop = shell.SpecialFolders("Desktop")
            return desktop
        except Exception as e:
            logger.warning(f"无法获取桌面路径: {e}")
            return os.path.join(os.path.expanduser("~"), "Desktop")
    
    def scan_desktop_files(self) -> List[Dict[str, Any]]:
        """扫描桌面上的文件和快捷方式"""
        files = []
        
        if not os.path.exists(self.desktop_path):
            logger.warning(f"桌面路径不存在: {self.desktop_path}")
            return files
        
        try:
            for item in os.listdir(self.desktop_path):
                item_path = os.path.join(self.desktop_path, item)
                
                if item.startswith('.') or item.startswith('~'):
                    continue
                
                if os.path.isfile(item_path):
                    file_info = self._analyze_file(item_path)
                    if file_info:
                        files.append(file_info)
                
                elif item.lower().endswith('.lnk'):
                    shortcut_info = self._analyze_shortcut(item_path)
                    if shortcut_info:
                        files.append(shortcut_info)
        
        except Exception as e:
            logger.error(f"扫描桌面文件时出错: {e}")
        
        return files
    
    def _analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """分析文件信息"""
        try:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext not in self.supported_extensions:
                return None
            
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            file_info = {
                'name': file_name,
                'path': file_path,
                'type': 'file',
                'extension': file_ext,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'executable': file_ext in ['.exe', '.bat', '.cmd', '.py', '.pyw'],
                'launchable': True
            }
            
            if file_ext in ['.py', '.pyw']:
                file_info['python_script'] = True
                file_info['description'] = f"Python脚本: {file_name}"
            elif file_ext in ['.bat', '.cmd']:
                file_info['batch_script'] = True
                file_info['description'] = f"批处理文件: {file_name}"
            elif file_ext == '.exe':
                file_info['executable_file'] = True
                file_info['description'] = f"可执行程序: {file_name}"
            
            return file_info
            
        except Exception as e:
            logger.error(f"分析文件 {file_path} 时出错: {e}")
            return None
    
    def _analyze_shortcut(self, shortcut_path: str) -> Optional[Dict[str, Any]]:
        """分析快捷方式信息"""
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            
            target_path = shortcut.Targetpath
            if not target_path or not os.path.exists(target_path):
                return None
            
            file_name = os.path.basename(shortcut_path)
            target_name = os.path.basename(target_path)
            target_ext = os.path.splitext(target_path)[1].lower()
            
            shortcut_info = {
                'name': file_name,
                'path': shortcut_path,
                'type': 'shortcut',
                'target_path': target_path,
                'target_name': target_name,
                'target_extension': target_ext,
                'description': shortcut.Description or f"快捷方式: {target_name}",
                'working_directory': shortcut.WorkingDirectory or os.path.dirname(target_path),
                'arguments': shortcut.Arguments or "",
                'launchable': True,
                'executable': target_ext in ['.exe', '.bat', '.cmd', '.py', '.pyw']
            }
            
            return shortcut_info
            
        except Exception as e:
            logger.error(f"分析快捷方式 {shortcut_path} 时出错: {e}")
            return None
    
    def safe_launch_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """安全启动文件或快捷方式，避免黑屏问题"""
        try:
            file_path = file_info.get('path')
            file_type = file_info.get('type')
            target_path = file_info.get('target_path') if file_type == 'shortcut' else file_path
            
            if not target_path or not os.path.exists(target_path):
                return {
                    'success': False,
                    'error': f"文件不存在: {target_path}",
                    'file_info': file_info
                }
            
            # 检查是否为Steam
            if 'steam' in target_path.lower():
                return self._safe_launch_steam(file_info)
            
            # 根据文件类型选择启动方式
            if file_type == 'shortcut':
                return self._safe_launch_shortcut(file_info)
            else:
                return self._safe_launch_file(file_info)
                
        except Exception as e:
            logger.error(f"启动文件时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_info': file_info
            }
    
    def _safe_launch_steam(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """安全启动Steam，避免黑屏"""
        try:
            target_path = file_info.get('target_path', file_info.get('path'))
            
            logger.info(f"安全启动Steam: {target_path}")
            
            # 使用os.startfile而不是subprocess，避免控制台创建
            os.startfile(target_path)
            
            return {
                'success': True,
                'method': 'os_startfile',
                'file_path': target_path,
                'message': 'Steam安全启动成功'
            }
            
        except Exception as e:
            logger.error(f"安全启动Steam失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_info': file_info
            }
    
    def _safe_launch_shortcut(self, shortcut_info: Dict[str, Any]) -> Dict[str, Any]:
        """安全启动快捷方式"""
        try:
            target_path = shortcut_info['target_path']
            working_dir = shortcut_info.get('working_directory', os.path.dirname(target_path))
            arguments = shortcut_info.get('arguments', '')
            
            # 对于Steam等游戏应用，使用os.startfile
            if any(keyword in target_path.lower() for keyword in ['steam', 'game', 'epic', 'origin']):
                os.startfile(target_path)
                return {
                    'success': True,
                    'method': 'os_startfile',
                    'file_path': target_path,
                    'file_info': shortcut_info
                }
            
            # 其他应用使用subprocess，但不创建新控制台
            if arguments:
                cmd = f'"{target_path}" {arguments}'
            else:
                cmd = f'"{target_path}"'
            
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                shell=True,
                # 移除CREATE_NEW_CONSOLE标志，避免黑屏
                creationflags=0
            )
            
            return {
                'success': True,
                'process_id': process.pid,
                'command': cmd,
                'working_directory': working_dir,
                'file_info': shortcut_info
            }
            
        except Exception as e:
            logger.error(f"启动快捷方式时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_info': shortcut_info
            }
    
    def _safe_launch_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """安全启动文件"""
        try:
            file_path = file_info['path']
            file_ext = file_info['extension']
            working_dir = os.path.dirname(file_path)
            
            if file_ext == '.exe':
                # 可执行文件使用os.startfile
                os.startfile(file_path)
                process = None
                
            elif file_ext in ['.bat', '.cmd']:
                # 批处理文件
                process = subprocess.Popen(
                    file_path,
                    cwd=working_dir,
                    shell=True,
                    creationflags=0  # 不创建新控制台
                )
                
            elif file_ext in ['.py', '.pyw']:
                # Python脚本
                python_exe = sys.executable
                process = subprocess.Popen(
                    [python_exe, file_path],
                    cwd=working_dir,
                    creationflags=0  # 不创建新控制台
                )
                
            elif file_ext == '.url':
                # URL文件
                os.startfile(file_path)
                process = None
                
            else:
                # 其他文件类型
                os.startfile(file_path)
                process = None
            
            return {
                'success': True,
                'process_id': process.pid if process else None,
                'file_path': file_path,
                'working_directory': working_dir,
                'file_info': file_info
            }
            
        except Exception as e:
            logger.error(f"启动文件时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_info': file_info
            }
    
    def search_files(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索桌面文件"""
        all_files = self.scan_desktop_files()
        
        if not keyword:
            return all_files
        
        keyword = keyword.lower()
        matched_files = []
        
        for file_info in all_files:
            if keyword in file_info['name'].lower():
                matched_files.append(file_info)
                continue
            
            description = file_info.get('description', '').lower()
            if keyword in description:
                matched_files.append(file_info)
                continue
            
            if file_info.get('type') == 'shortcut':
                target_name = file_info.get('target_name', '').lower()
                if keyword in target_name:
                    matched_files.append(file_info)
        
        return matched_files



