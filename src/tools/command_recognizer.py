#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """命令类型枚举"""
    DESKTOP_SCAN = "desktop_scan"
    DESKTOP_SEARCH = "desktop_search"
    DESKTOP_LAUNCH = "desktop_launch"
    WEB_SEARCH = "web_search"
    WEB_BROWSE = "web_browse"
    WEB_AUTOMATE = "web_automate"
    BILIBILI_OPERATION = "bilibili_operation"
    FILE_OPERATION = "file_operation"
    SYSTEM_COMMAND = "system_command"
    CALCULATION = "calculation"
    TRANSLATION = "translation"
    GENERAL_QUERY = "general_query"


class CommandRecognizer:
    """智能命令识别器"""
    
    def __init__(self):
        # 桌面操作关键词
        self.desktop_keywords = {
            'scan': ['扫描', 'scan', '查看', '显示', '列出', 'list'],
            'search': ['搜索', 'search', '查找', '找', 'find'],
            'launch': ['启动', 'launch', '运行', 'run', '打开', 'open', '执行', 'execute']
        }
        
        # 网络操作关键词
        self.web_keywords = {
            'search': ['搜索', 'search', '查找', '找', 'find'],
            'browse': ['浏览', 'browse', '访问', 'visit', '打开网站', 'open website'],
            'automate': ['自动化', 'automate', '操作', 'operate', '点击', 'click']
        }
        
        # B站操作关键词
        self.bilibili_keywords = {
            'search_play': ['搜索播放', 'search play', '播放', 'play', '看视频', 'watch video', '搜索', 'search'],
            'up_homepage': ['UP主页', 'up homepage', '主页', 'homepage', '个人主页']
        }
        
        # 文件操作关键词
        self.file_keywords = {
            'create': ['创建', 'create', '新建', 'new', '建立', 'make'],
            'read': ['读取', 'read', '打开', 'open', '查看', 'view'],
            'write': ['写入', 'write', '保存', 'save', '存储', 'store'],
            'delete': ['删除', 'delete', '移除', 'remove', '清除', 'clear']
        }
        
        # 系统命令关键词
        self.system_keywords = {
            'command': ['命令', 'command', '执行', 'execute', '运行', 'run'],
            'process': ['进程', 'process', '程序', 'program', '应用', 'app']
        }
        
        # 计算关键词
        self.calculation_keywords = ['计算', 'calculate', '算', '数学', 'math', '+', '-', '*', '/', '=']
        
        # 翻译关键词
        self.translation_keywords = ['翻译', 'translate', '转换', 'convert', '英文', '中文', 'english', 'chinese']
    
    def recognize_command(self, user_input: str) -> Tuple[CommandType, Dict[str, Any]]:
        """识别用户输入的命令类型和参数"""
        user_input = user_input.strip().lower()
        
        # B站操作识别（优先级最高，因为B站是特定网站）
        bilibili_result = self._recognize_bilibili_command(user_input)
        if bilibili_result:
            return bilibili_result
        
        # 桌面操作识别
        desktop_result = self._recognize_desktop_command(user_input)
        if desktop_result:
            return desktop_result
        
        # 网络操作识别
        web_result = self._recognize_web_command(user_input)
        if web_result:
            return web_result
        
        # 文件操作识别
        file_result = self._recognize_file_command(user_input)
        if file_result:
            return file_result
        
        # 系统命令识别
        system_result = self._recognize_system_command(user_input)
        if system_result:
            return system_result
        
        # 计算识别
        if self._is_calculation(user_input):
            return CommandType.CALCULATION, {'expression': user_input}
        
        # 翻译识别
        if self._is_translation(user_input):
            return CommandType.TRANSLATION, {'text': user_input}
        
        # 默认返回通用查询
        return CommandType.GENERAL_QUERY, {'query': user_input}
    
    def _recognize_desktop_command(self, user_input: str) -> Optional[Tuple[CommandType, Dict[str, Any]]]:
        """识别桌面操作命令"""
        # 扫描桌面
        if any(keyword in user_input for keyword in self.desktop_keywords['scan'] + ['桌面', 'desktop']):
            if any(keyword in user_input for keyword in ['文件', 'file', '应用', 'app']):
                return CommandType.DESKTOP_SCAN, {'action': 'scan_files'}
        
        # 搜索桌面
        if any(keyword in user_input for keyword in self.desktop_keywords['search']):
            if any(keyword in user_input for keyword in ['桌面', 'desktop']):
                # 提取搜索关键词
                keyword = self._extract_search_keyword(user_input, self.desktop_keywords['search'])
                if keyword:
                    return CommandType.DESKTOP_SEARCH, {'action': 'search_files', 'keyword': keyword}
        
        # 启动桌面文件
        if any(keyword in user_input for keyword in self.desktop_keywords['launch']):
            if any(keyword in user_input for keyword in ['桌面', 'desktop', '文件', 'file', '应用', 'app']):
                # 提取文件名
                filename = self._extract_filename(user_input, self.desktop_keywords['launch'])
                if filename:
                    return CommandType.DESKTOP_LAUNCH, {'action': 'launch_file', 'filename': filename}
        
        return None
    
    def _recognize_web_command(self, user_input: str) -> Optional[Tuple[CommandType, Dict[str, Any]]]:
        """识别网络操作命令"""
        # 网络搜索
        if any(keyword in user_input for keyword in self.web_keywords['search']):
            if any(keyword in user_input for keyword in ['网络', 'web', '互联网', 'internet', '在线', 'online']):
                keyword = self._extract_search_keyword(user_input, self.web_keywords['search'])
                if keyword:
                    return CommandType.WEB_SEARCH, {'action': 'web_search', 'keyword': keyword}
        
        # 网页浏览
        if any(keyword in user_input for keyword in self.web_keywords['browse']):
            if any(keyword in user_input for keyword in ['网页', 'webpage', '网站', 'website', '页面', 'page']):
                url = self._extract_url(user_input)
                if url:
                    return CommandType.WEB_BROWSE, {'action': 'browse_page', 'url': url}
        
        # 网页自动化
        if any(keyword in user_input for keyword in self.web_keywords['automate']):
            if any(keyword in user_input for keyword in ['网页', 'webpage', '网站', 'website']):
                return CommandType.WEB_AUTOMATE, {'action': 'web_automate', 'query': user_input}
        
        return None
    
    def _recognize_bilibili_command(self, user_input: str) -> Optional[Tuple[CommandType, Dict[str, Any]]]:
        """识别B站操作命令"""
        if any(keyword in user_input for keyword in ['b站', 'bilibili', '哔哩哔哩', '打开b站', '打开bilibili', 'b站搜索', 'b站播放']):
            # 搜索播放
            if any(keyword in user_input for keyword in self.bilibili_keywords['search_play']):
                keyword = self._extract_search_keyword(user_input, self.bilibili_keywords['search_play'])
                if keyword:
                    return CommandType.BILIBILI_OPERATION, {'action': 'search_play', 'keyword': keyword}
            
            # UP主页
            if any(keyword in user_input for keyword in self.bilibili_keywords['up_homepage']):
                up_name = self._extract_up_name(user_input)
                if up_name:
                    return CommandType.BILIBILI_OPERATION, {'action': 'up_homepage', 'up_name': up_name}
        
        return None
    
    def _recognize_file_command(self, user_input: str) -> Optional[Tuple[CommandType, Dict[str, Any]]]:
        """识别文件操作命令"""
        # 创建文件
        if any(keyword in user_input for keyword in self.file_keywords['create']):
            if any(keyword in user_input for keyword in ['文件', 'file', '文档', 'document']):
                filename = self._extract_filename(user_input, self.file_keywords['create'])
                if filename:
                    return CommandType.FILE_OPERATION, {'action': 'create_file', 'filename': filename}
        
        # 读取文件
        if any(keyword in user_input for keyword in self.file_keywords['read']):
            if any(keyword in user_input for keyword in ['文件', 'file', '文档', 'document']):
                filename = self._extract_filename(user_input, self.file_keywords['read'])
                if filename:
                    return CommandType.FILE_OPERATION, {'action': 'read_file', 'filename': filename}
        
        return None
    
    def _recognize_system_command(self, user_input: str) -> Optional[Tuple[CommandType, Dict[str, Any]]]:
        """识别系统命令"""
        if any(keyword in user_input for keyword in self.system_keywords['command']):
            command = self._extract_system_command(user_input)
            if command:
                return CommandType.SYSTEM_COMMAND, {'action': 'execute_command', 'command': command}
        
        return None
    
    def _is_calculation(self, user_input: str) -> bool:
        """判断是否为计算表达式"""
        # 检查是否包含数学运算符
        if any(op in user_input for op in ['+', '-', '*', '/', '=', '(', ')']):
            return True
        
        # 检查是否包含计算关键词
        if any(keyword in user_input for keyword in self.calculation_keywords):
            return True
        
        return False
    
    def _is_translation(self, user_input: str) -> bool:
        """判断是否为翻译请求"""
        return any(keyword in user_input for keyword in self.translation_keywords)
    
    def _extract_search_keyword(self, user_input: str, action_keywords: List[str]) -> Optional[str]:
        """提取搜索关键词"""
        # 移除动作关键词，提取剩余部分作为搜索关键词
        for keyword in action_keywords:
            user_input = user_input.replace(keyword, '').strip()
        
        # 移除其他常见词汇
        common_words = ['桌面', 'desktop', '文件', 'file', '搜索', 'search', '查找', 'find']
        for word in common_words:
            user_input = user_input.replace(word, '').strip()
        
        # 清理多余的空格和标点
        user_input = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', user_input)
        user_input = ' '.join(user_input.split())
        
        return user_input if user_input else None
    
    def _extract_filename(self, user_input: str, action_keywords: List[str]) -> Optional[str]:
        """提取文件名"""
        # 移除动作关键词
        for keyword in action_keywords:
            user_input = user_input.replace(keyword, '').strip()
        
        # 移除其他常见词汇
        common_words = ['桌面', 'desktop', '文件', 'file', '应用', 'app', '启动', 'launch', '运行', 'run']
        for word in common_words:
            user_input = user_input.replace(word, '').strip()
        
        # 清理多余的空格和标点
        user_input = re.sub(r'[^\w\s\u4e00-\u9fff.-]', ' ', user_input)
        user_input = ' '.join(user_input.split())
        
        return user_input if user_input else None
    
    def _extract_url(self, user_input: str) -> Optional[str]:
        """提取URL"""
        # 使用正则表达式匹配URL
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, user_input)
        if match:
            return match.group(0)
        
        # 如果没有找到完整URL，尝试提取域名
        domain_pattern = r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(domain_pattern, user_input)
        if match:
            return f"https://{match.group(0)}"
        
        return None
    
    def _extract_up_name(self, user_input: str) -> Optional[str]:
        """提取UP主名称"""
        # 移除B站相关词汇
        bilibili_words = ['b站', 'bilibili', '哔哩哔哩', 'UP主页', 'up homepage', '主页', 'homepage']
        for word in bilibili_words:
            user_input = user_input.replace(word, '').strip()
        
        # 清理多余的空格和标点
        user_input = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', user_input)
        user_input = ' '.join(user_input.split())
        
        return user_input if user_input else None
    
    def _extract_system_command(self, user_input: str) -> Optional[str]:
        """提取系统命令"""
        # 移除命令相关词汇
        command_words = ['命令', 'command', '执行', 'execute', '运行', 'run']
        for word in command_words:
            user_input = user_input.replace(word, '').strip()
        
        # 清理多余的空格和标点
        user_input = re.sub(r'[^\w\s\u4e00-\u9fff.-]', ' ', user_input)
        user_input = ' '.join(user_input.split())
        
        return user_input if user_input else None
    
    def get_command_suggestions(self, user_input: str) -> List[str]:
        """获取命令建议"""
        suggestions = []
        user_input_lower = user_input.lower()
        
        # 桌面操作建议
        if any(keyword in user_input_lower for keyword in ['桌面', 'desktop']):
            suggestions.extend([
                "扫描桌面文件",
                "搜索桌面文件 [关键词]",
                "启动桌面文件 [文件名]"
            ])
        
        # 网络操作建议
        if any(keyword in user_input_lower for keyword in ['搜索', 'search', '网络', 'web']):
            suggestions.extend([
                "搜索网络信息 [关键词]",
                "打开网站 [URL]",
                "网页自动化操作"
            ])
        
        # B站操作建议
        if any(keyword in user_input_lower for keyword in ['b站', 'bilibili', '视频', 'video']):
            suggestions.extend([
                "B站搜索播放 [关键词]",
                "打开UP主主页 [UP名称]"
            ])
        
        # 文件操作建议
        if any(keyword in user_input_lower for keyword in ['文件', 'file', '创建', 'create']):
            suggestions.extend([
                "创建文件 [文件名]",
                "读取文件 [文件名]",
                "保存文件 [文件名]"
            ])
        
        return suggestions[:5]  # 返回前5个建议


def main():
    """测试命令识别器"""
    recognizer = CommandRecognizer()
    
    test_commands = [
        "扫描桌面文件",
        "搜索桌面文件 python",
        "启动桌面文件 notepad.exe",
        "搜索网络信息 人工智能",
        "打开网站 https://www.example.com",
        "B站搜索播放 影视飓风",
        "打开UP主主页 影视飓风",
        "创建文件 test.txt",
        "计算 2+3*4",
        "翻译 hello world",
        "运行命令 dir",
        "今天天气怎么样？"
    ]
    
    print("命令识别测试:")
    print("=" * 50)
    
    for command in test_commands:
        cmd_type, params = recognizer.recognize_command(command)
        print(f"输入: {command}")
        print(f"类型: {cmd_type.value}")
        print(f"参数: {params}")
        print("-" * 30)


if __name__ == "__main__":
    main()



