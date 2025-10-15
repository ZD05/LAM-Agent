#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from .desktop_launcher_safe import SafeDesktopLauncher

logger = logging.getLogger(__name__)


class DesktopIntegration:
    """桌面集成类，将桌面启动功能集成到LAM Agent中"""
    
    def __init__(self):
        self.launcher = SafeDesktopLauncher()
    
    def handle_desktop_command(self, command: str) -> Dict[str, Any]:
        """处理桌面相关命令"""
        command = command.lower().strip()
        
        if '扫描桌面' in command or 'scan desktop' in command:
            return self.scan_desktop()
        elif '搜索桌面' in command or 'search desktop' in command:
            return self.search_desktop(command)
        elif '启动' in command or 'launch' in command:
            return self.launch_from_command(command)
        else:
            return {
                'success': False,
                'error': '未知的桌面命令',
                'available_commands': [
                    '扫描桌面文件',
                    '搜索桌面文件 [关键词]',
                    '启动桌面文件 [文件名]'
                ]
            }
    
    def scan_desktop(self) -> Dict[str, Any]:
        """扫描桌面文件"""
        try:
            files = self.launcher.scan_desktop_files()
            
            if not files:
                return {
                    'success': True,
                    'message': '桌面上没有找到可启动的文件或快捷方式',
                    'files': []
                }
            
            # 格式化文件信息
            file_list = []
            for file_info in files:
                file_list.append({
                    'name': file_info['name'],
                    'type': file_info['type'],
                    'description': file_info.get('description', ''),
                    'executable': file_info.get('executable', False),
                    'size_mb': file_info.get('size_mb', 0)
                })
            
            return {
                'success': True,
                'message': f'在桌面上找到 {len(files)} 个可启动的文件/快捷方式',
                'files': file_list,
                'total_count': len(files)
            }
            
        except Exception as e:
            logger.error(f"扫描桌面时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_desktop(self, command: str) -> Dict[str, Any]:
        """搜索桌面文件"""
        try:
            # 提取搜索关键词
            keyword = self._extract_keyword(command, ['搜索桌面', 'search desktop'])
            
            if not keyword:
                return {
                    'success': False,
                    'error': '请提供搜索关键词',
                    'usage': '搜索桌面文件 [关键词]'
                }
            
            files = self.launcher.search_files(keyword)
            
            if not files:
                return {
                    'success': True,
                    'message': f'没有找到包含 "{keyword}" 的文件',
                    'files': [],
                    'keyword': keyword
                }
            
            # 格式化文件信息
            file_list = []
            for file_info in files:
                file_list.append({
                    'name': file_info['name'],
                    'type': file_info['type'],
                    'description': file_info.get('description', ''),
                    'executable': file_info.get('executable', False),
                    'path': file_info['path']
                })
            
            return {
                'success': True,
                'message': f'找到 {len(files)} 个包含 "{keyword}" 的文件',
                'files': file_list,
                'keyword': keyword,
                'total_count': len(files)
            }
            
        except Exception as e:
            logger.error(f"搜索桌面时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def launch_from_command(self, command: str) -> Dict[str, Any]:
        """从命令中启动文件"""
        try:
            # 提取文件名
            filename = self._extract_keyword(command, ['启动', 'launch'])
            
            if not filename:
                return {
                    'success': False,
                    'error': '请提供要启动的文件名',
                    'usage': '启动桌面文件 [文件名]'
                }
            
            # 搜索匹配的文件
            files = self.launcher.search_files(filename)
            
            if not files:
                return {
                    'success': False,
                    'error': f'没有找到名为 "{filename}" 的文件',
                    'suggestion': '请使用"扫描桌面文件"查看所有可用文件'
                }
            
            # 如果找到多个匹配文件，选择第一个
            if len(files) > 1:
                logger.info(f"找到多个匹配文件，选择第一个: {files[0]['name']}")
            
            target_file = files[0]
            
            # 启动文件
            result = self.launcher.launch_file(target_file)
            
            if result['success']:
                return {
                    'success': True,
                    'message': f'成功启动: {target_file["name"]}',
                    'file_info': {
                        'name': target_file['name'],
                        'type': target_file['type'],
                        'description': target_file.get('description', '')
                    },
                    'launch_result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'启动失败: {result.get("error", "未知错误")}',
                    'file_info': target_file
                }
                
        except Exception as e:
            logger.error(f"启动文件时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_keyword(self, command: str, prefixes: List[str]) -> str:
        """从命令中提取关键词"""
        command = command.strip()
        
        for prefix in prefixes:
            if command.startswith(prefix):
                keyword = command[len(prefix):].strip()
                return keyword
        
        return ""
    
    def get_desktop_files_summary(self) -> Dict[str, Any]:
        """获取桌面文件摘要"""
        try:
            files = self.launcher.scan_desktop_files()
            
            # 统计文件类型
            type_stats = {}
            executable_count = 0
            
            for file_info in files:
                file_type = file_info['type']
                type_stats[file_type] = type_stats.get(file_type, 0) + 1
                
                if file_info.get('executable', False):
                    executable_count += 1
            
            return {
                'success': True,
                'total_files': len(files),
                'executable_files': executable_count,
                'type_statistics': type_stats,
                'desktop_path': self.launcher.desktop_path
            }
            
        except Exception as e:
            logger.error(f"获取桌面文件摘要时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """测试桌面集成功能"""
    print("=" * 60)
    print("桌面集成功能测试")
    print("=" * 60)
    
    integration = DesktopIntegration()
    
    # 测试扫描桌面
    print("1. 测试扫描桌面:")
    result = integration.scan_desktop()
    print(f"结果: {result['success']}")
    if result['success']:
        print(f"消息: {result['message']}")
        print(f"文件数量: {result['total_count']}")
    else:
        print(f"错误: {result['error']}")
    
    print("\n" + "-" * 40)
    
    # 测试搜索桌面
    print("2. 测试搜索桌面 (关键词: 'python'):")
    result = integration.search_desktop("搜索桌面 python")
    print(f"结果: {result['success']}")
    if result['success']:
        print(f"消息: {result['message']}")
        print(f"匹配数量: {result['total_count']}")
    else:
        print(f"错误: {result['error']}")
    
    print("\n" + "-" * 40)
    
    # 测试获取摘要
    print("3. 测试获取桌面文件摘要:")
    result = integration.get_desktop_files_summary()
    print(f"结果: {result['success']}")
    if result['success']:
        print(f"总文件数: {result['total_files']}")
        print(f"可执行文件数: {result['executable_files']}")
        print(f"类型统计: {result['type_statistics']}")
        print(f"桌面路径: {result['desktop_path']}")
    else:
        print(f"错误: {result['error']}")


if __name__ == "__main__":
    main()



