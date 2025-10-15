#!/usr/bin/env python3
"""
LAM-Agent MCP服务器实现
提供标准化的MCP协议接口，将现有工具转换为MCP工具
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.tools.executor import executor
from src.tools.browser import fetch_page, automate_page
from src.tools.bilibili_integration import BilibiliIntegration
from src.tools.desktop_launcher_safe import SafeDesktopLauncher
from src.tools.search import web_search
from src.tools.steam_integration import steam_integration
from src.tools.bilibili_integration import bilibili_integration
from .core.base import MCPTool

logger = logging.getLogger(__name__)

class LAMMCPServer:
    """LAM-Agent MCP服务器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.desktop_launcher = SafeDesktopLauncher()
        self._register_tools()
    
    def _register_tools(self):
        """注册所有MCP工具"""
        
        # 注册自动登录工具
        self._register_auto_login_tools()
        
        # 网页自动化工具
        self.tools["web_automate"] = MCPTool(
            name="web_automate",
            description="在指定网页上执行自动化操作",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标网页URL"},
                    "steps": {
                        "type": "array",
                        "description": "操作步骤列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["click", "type", "wait", "sleep", "scroll", "press"]},
                                "selector": {"type": "string", "description": "CSS选择器"},
                                "text": {"type": "string", "description": "要输入的文本"},
                                "key": {"type": "string", "description": "要按下的键盘按键"},
                                "ms": {"type": "integer", "description": "等待时间（毫秒）"}
                            },
                            "required": ["action"]
                        }
                    }
                },
                "required": ["url"]
            },
            handler=self._handle_web_automate
        )
        
        # B站搜索播放工具
        self.tools["bilibili_search_play"] = MCPTool(
            name="bilibili_search_play",
            description="在B站搜索UP主并播放其第一个视频",
            input_schema={
                "type": "object",
                "properties": {
                    "up_name": {"type": "string", "description": "UP主名称"},
                    "keep_open_seconds": {"type": "number", "description": "保持页面打开的时间（秒）", "default": 60}
                },
                "required": ["up_name"]
            },
            handler=self._handle_bilibili_search_play
        )
        
        # 桌面文件管理工具
        self.tools["desktop_scan"] = MCPTool(
            name="desktop_scan",
            description="扫描桌面文件和快捷方式",
            input_schema={
                "type": "object",
                "properties": {
                    "file_type": {"type": "string", "description": "文件类型过滤", "default": "all"}
                }
            },
            handler=self._handle_desktop_scan
        )
        
        self.tools["desktop_launch"] = MCPTool(
            name="desktop_launch",
            description="启动桌面上的文件或应用程序",
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "要启动的文件名"},
                    "exact_match": {"type": "boolean", "description": "是否精确匹配文件名", "default": False}
                },
                "required": ["filename"]
            },
            handler=self._handle_desktop_launch
        )
        
        # 网络搜索工具
        self.tools["web_search"] = MCPTool(
            name="web_search",
            description="使用DuckDuckGo进行网络搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"},
                    "max_results": {"type": "integer", "description": "最大结果数量", "default": 5}
                },
                "required": ["query"]
            },
            handler=self._handle_web_search
        )
        
        # 文件操作工具
        self.tools["file_read"] = MCPTool(
            name="file_read",
            description="读取文件内容",
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件路径"}
                },
                "required": ["filename"]
            },
            handler=self._handle_file_read
        )
        
        self.tools["file_write"] = MCPTool(
            name="file_write",
            description="写入文件内容",
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["filename", "content"]
            },
            handler=self._handle_file_write
        )
        
        # 系统命令工具
        self.tools["run_command"] = MCPTool(
            name="run_command",
            description="执行系统命令",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"},
                    "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 30}
                },
                "required": ["command"]
            },
            handler=self._handle_run_command
        )
        
        # 网页内容抓取工具
        self.tools["fetch_page"] = MCPTool(
            name="fetch_page",
            description="抓取网页内容",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网页URL"},
                    "wait_selector": {"type": "string", "description": "等待的选择器"},
                    "timeout_ms": {"type": "integer", "description": "超时时间（毫秒）", "default": 15000}
                },
                "required": ["url"]
            },
            handler=self._handle_fetch_page
        )
        
        # 网站打开工具
        self.tools["open_website"] = MCPTool(
            name="open_website",
            description="在浏览器中打开网站",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要打开的网站URL"}
                },
                "required": ["url"]
            },
            handler=self._handle_open_website
        )
        
        # B站打开工具
        self.tools["open_bilibili"] = MCPTool(
            name="open_bilibili",
            description="打开B站并跳转到热门视频页面",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_open_bilibili
        )
        
        # 视频播放工具
        self.tools["play_video"] = MCPTool(
            name="play_video",
            description="播放视频",
            input_schema={
                "type": "object",
                "properties": {
                    "video_url": {"type": "string", "description": "视频URL"},
                    "platform": {"type": "string", "description": "平台名称", "default": "bilibili"},
                    "query": {"type": "string", "description": "搜索查询"}
                }
            },
            handler=self._handle_play_video
        )
        
        # 自然语言自动化工具
        self.tools["nl_automate"] = MCPTool(
            name="nl_automate",
            description="将自然语言解析为自动化操作并执行",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "自然语言指令"},
                    "url": {"type": "string", "description": "目标站点初始URL"},
                    "auth": {
                        "type": "object",
                        "description": "认证信息",
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                            "username_selector": {"type": "string"},
                            "password_selector": {"type": "string"},
                            "submit_selector": {"type": "string"}
                        }
                    },
                    "steps": {
                        "type": "array",
                        "description": "额外步骤",
                        "items": {"type": "object"}
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_nl_automate
        )
        
        # 站点搜索工具
        self.tools["site_search"] = MCPTool(
            name="site_search",
            description="在指定网站内搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标网站URL"},
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "click_first_result": {"type": "boolean", "description": "是否点击第一个结果", "default": True}
                },
                "required": ["url", "keyword"]
            },
            handler=self._handle_site_search
        )
        
        # 商品浏览工具
        self.tools["browse_product"] = MCPTool(
            name="browse_product",
            description="浏览商品详情",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "商品页面URL"},
                    "keyword": {"type": "string", "description": "商品关键词"},
                    "match_text": {"type": "string", "description": "匹配文本"}
                },
                "required": ["url", "keyword"]
            },
            handler=self._handle_browse_product
        )
        
        # 通用视频播放工具
        self.tools["play_video_generic"] = MCPTool(
            name="play_video_generic",
            description="通用视频播放",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "视频页面URL"},
                    "keyword": {"type": "string", "description": "视频关键词"},
                    "match_text": {"type": "string", "description": "匹配文本"}
                },
                "required": ["url", "keyword"]
            },
            handler=self._handle_play_video_generic
        )
        
        # 加入购物车工具
        self.tools["add_to_cart"] = MCPTool(
            name="add_to_cart",
            description="将商品加入购物车",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "商品页面URL"},
                    "keyword": {"type": "string", "description": "商品关键词"},
                    "match_text": {"type": "string", "description": "匹配文本"}
                },
                "required": ["url", "keyword"]
            },
            handler=self._handle_add_to_cart
        )
        
        # B站UP主页工具
        self.tools["bilibili_open_up"] = MCPTool(
            name="bilibili_open_up",
            description="打开B站UP主主页",
            input_schema={
                "type": "object",
                "properties": {
                    "up_name": {"type": "string", "description": "UP主名称"},
                    "keep_open_seconds": {"type": "number", "description": "保持页面打开的时间（秒）", "default": 60}
                },
                "required": ["up_name"]
            },
            handler=self._handle_bilibili_open_up
        )
        
        # 自然语言步骤执行工具
        self.tools["nl_step_execute"] = MCPTool(
            name="nl_step_execute",
            description="执行自然语言指令的步骤化操作",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "自然语言指令"}
                },
                "required": ["query"]
            },
            handler=self._handle_nl_step_execute
        )
        
        # 天气查询工具
        self.tools["get_weather"] = MCPTool(
            name="get_weather",
            description="获取天气信息",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称", "default": "北京"}
                }
            },
            handler=self._handle_get_weather
        )
        
        # 数学计算工具
        self.tools["calculate"] = MCPTool(
            name="calculate",
            description="计算数学表达式",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            },
            handler=self._handle_calculate
        )
        
        # 翻译工具
        self.tools["translate"] = MCPTool(
            name="translate",
            description="翻译文本",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要翻译的文本"},
                    "target_lang": {"type": "string", "description": "目标语言", "default": "en"}
                },
                "required": ["text"]
            },
            handler=self._handle_translate
        )
        
        # 邮件发送工具
        self.tools["send_email"] = MCPTool(
            name="send_email",
            description="发送邮件",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "收件人"},
                    "subject": {"type": "string", "description": "邮件主题"},
                    "content": {"type": "string", "description": "邮件内容"}
                },
                "required": ["to", "subject", "content"]
            },
            handler=self._handle_send_email
        )
        
        # 任务调度工具
        self.tools["schedule_task"] = MCPTool(
            name="schedule_task",
            description="安排任务",
            input_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "任务描述"},
                    "time": {"type": "string", "description": "执行时间"}
                },
                "required": ["task"]
            },
            handler=self._handle_schedule_task
        )
        
        # Steam集成工具
        self.tools["steam_get_library"] = MCPTool(
            name="steam_get_library",
            description="获取Steam游戏库和详细统计信息",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_steam_get_library
        )
        
        self.tools["steam_get_recent_activity"] = MCPTool(
            name="steam_get_recent_activity",
            description="查看最近的游戏活动和当前正在玩的游戏",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_steam_get_recent_activity
        )
        
        self.tools["steam_get_game_details"] = MCPTool(
            name="steam_get_game_details",
            description="获取详细的游戏信息和成就",
            input_schema={
                "type": "object",
                "properties": {
                    "appid": {"type": "string", "description": "游戏应用ID"}
                },
                "required": ["appid"]
            },
            handler=self._handle_steam_get_game_details
        )
        
        self.tools["steam_get_friend_comparison"] = MCPTool(
            name="steam_get_friend_comparison",
            description="与朋友比较游戏库并获得推荐",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_steam_get_friend_comparison
        )
        
        self.tools["steam_open_store"] = MCPTool(
            name="steam_open_store",
            description="打开Steam商店，优先尝试桌面快捷方式，如果不存在则在浏览器中打开",
            input_schema={
                "type": "object",
                "properties": {
                    "game_name": {"type": "string", "description": "游戏名称（可选）"}
                }
            },
            handler=self._handle_steam_open_store
        )
        
        self.tools["steam_analyze_habits"] = MCPTool(
            name="steam_analyze_habits",
            description="分析游戏习惯和偏好",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_steam_analyze_habits
        )
        
        self.tools["steam_get_recommendations"] = MCPTool(
            name="steam_get_recommendations",
            description="获取游戏推荐",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_steam_get_recommendations
        )
        
        self.tools["steam_download_game"] = MCPTool(
            name="steam_download_game",
            description="下载Steam游戏",
            input_schema={
                "type": "object",
                "properties": {
                    "appid": {"type": "string", "description": "游戏AppID"}
                },
                "required": ["appid"]
            },
            handler=self._handle_steam_download_game
        )
        
        self.tools["steam_uninstall_game"] = MCPTool(
            name="steam_uninstall_game",
            description="卸载Steam游戏",
            input_schema={
                "type": "object",
                "properties": {
                    "appid": {"type": "string", "description": "游戏AppID"}
                },
                "required": ["appid"]
            },
            handler=self._handle_steam_uninstall_game
        )
        
        # Bilibili集成工具
        self.tools["bilibili_get_user_profile"] = MCPTool(
            name="bilibili_get_user_profile",
            description="获取用户资料信息和统计数据",
            input_schema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "用户ID"}
                },
                "required": ["uid"]
            },
            handler=self._handle_bilibili_get_user_profile
        )
        
        self.tools["bilibili_search_videos"] = MCPTool(
            name="bilibili_search_videos",
            description="搜索视频并获取详细视频信息",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "page": {"type": "integer", "description": "页码", "default": 1},
                    "pagesize": {"type": "integer", "description": "每页数量", "default": 20}
                },
                "required": ["keyword"]
            },
            handler=self._handle_bilibili_search_videos
        )
        
        self.tools["bilibili_get_video_details"] = MCPTool(
            name="bilibili_get_video_details",
            description="获取视频详细信息",
            input_schema={
                "type": "object",
                "properties": {
                    "bvid": {"type": "string", "description": "视频BV号"}
                },
                "required": ["bvid"]
            },
            handler=self._handle_bilibili_get_video_details
        )
        
        self.tools["bilibili_get_user_videos"] = MCPTool(
            name="bilibili_get_user_videos",
            description="获取用户上传的视频",
            input_schema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "用户ID"},
                    "page": {"type": "integer", "description": "页码", "default": 1},
                    "pagesize": {"type": "integer", "description": "每页数量", "default": 20}
                },
                "required": ["uid"]
            },
            handler=self._handle_bilibili_get_user_videos
        )
        
        self.tools["bilibili_get_following_list"] = MCPTool(
            name="bilibili_get_following_list",
            description="获取关注列表",
            input_schema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "用户ID"},
                    "page": {"type": "integer", "description": "页码", "default": 1},
                    "pagesize": {"type": "integer", "description": "每页数量", "default": 20}
                },
                "required": ["uid"]
            },
            handler=self._handle_bilibili_get_following_list
        )
        
        self.tools["bilibili_get_favorites"] = MCPTool(
            name="bilibili_get_favorites",
            description="获取个人收藏",
            input_schema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "用户ID"},
                    "page": {"type": "integer", "description": "页码", "default": 1},
                    "pagesize": {"type": "integer", "description": "每页数量", "default": 20}
                },
                "required": ["uid"]
            },
            handler=self._handle_bilibili_get_favorites
        )
        
        self.tools["bilibili_get_watch_later"] = MCPTool(
            name="bilibili_get_watch_later",
            description="浏览稍后再看列表",
            input_schema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "页码", "default": 1},
                    "pagesize": {"type": "integer", "description": "每页数量", "default": 20}
                }
            },
            handler=self._handle_bilibili_get_watch_later
        )
        
        self.tools["bilibili_get_user_statistics"] = MCPTool(
            name="bilibili_get_user_statistics",
            description="获取用户统计数据",
            input_schema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "用户ID"}
                },
                "required": ["uid"]
            },
            handler=self._handle_bilibili_get_user_statistics
        )
        
        self.tools["bilibili_open_video"] = MCPTool(
            name="bilibili_open_video",
            description="打开B站视频",
            input_schema={
                "type": "object",
                "properties": {
                    "bvid": {"type": "string", "description": "视频BV号"}
                },
                "required": ["bvid"]
            },
            handler=self._handle_bilibili_open_video
        )
        
        self.tools["bilibili_open_user"] = MCPTool(
            name="bilibili_open_user",
            description="打开B站用户主页",
            input_schema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "用户ID"}
                },
                "required": ["uid"]
            },
            handler=self._handle_bilibili_open_user
        )
        
        # 网站集成工具
        self.tools["website_open"] = MCPTool(
            name="website_open",
            description="打开网站",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网站URL"}
                },
                "required": ["url"]
            },
            handler=self._handle_website_open
        )
        
        self.tools["website_search"] = MCPTool(
            name="website_search",
            description="在指定网站搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "website": {"type": "string", "description": "网站域名（可选）"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_website_search
        )
        
        self.tools["website_summary"] = MCPTool(
            name="website_summary",
            description="获取网站信息总结",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网站URL"}
                },
                "required": ["url"]
            },
            handler=self._handle_website_summary
        )
        
        # 京东专用工具
        self.tools["jd_search_products"] = MCPTool(
            name="jd_search_products",
            description="搜索京东商品",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "商品关键词"},
                    "page": {"type": "integer", "description": "页码（可选）"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_jd_search_products
        )
        
        self.tools["jd_get_product_info"] = MCPTool(
            name="jd_get_product_info",
            description="获取京东商品信息",
            input_schema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "商品ID"}
                },
                "required": ["product_id"]
            },
            handler=self._handle_jd_get_product_info
        )
        
        # 淘宝专用工具
        self.tools["taobao_search_products"] = MCPTool(
            name="taobao_search_products",
            description="搜索淘宝商品",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "商品关键词"},
                    "page": {"type": "integer", "description": "页码（可选）"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_taobao_search_products
        )
        
        self.tools["taobao_get_product_info"] = MCPTool(
            name="taobao_get_product_info",
            description="获取淘宝商品信息",
            input_schema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "商品ID"}
                },
                "required": ["product_id"]
            },
            handler=self._handle_taobao_get_product_info
        )
        
        # 高德地图专用工具
        self.tools["amap_search_location"] = MCPTool(
            name="amap_search_location",
            description="搜索高德地图位置",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "位置关键词"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_amap_search_location
        )
        
        self.tools["amap_get_route"] = MCPTool(
            name="amap_get_route",
            description="获取高德地图路线",
            input_schema={
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "起点"},
                    "end": {"type": "string", "description": "终点"},
                    "mode": {"type": "string", "description": "出行方式（driving/walking/transit）"}
                },
                "required": ["start", "end"]
            },
            handler=self._handle_amap_get_route
        )
        
        # 拼多多专用工具
        self.tools["pdd_search_products"] = MCPTool(
            name="pdd_search_products",
            description="搜索拼多多商品",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "商品关键词"},
                    "page": {"type": "integer", "description": "页码（可选）"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_pdd_search_products
        )
        
        self.tools["pdd_get_product_info"] = MCPTool(
            name="pdd_get_product_info",
            description="获取拼多多商品信息",
            input_schema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "商品ID"}
                },
                "required": ["product_id"]
            },
            handler=self._handle_pdd_get_product_info
        )
        
        # 抖音专用工具
        self.tools["douyin_search_videos"] = MCPTool(
            name="douyin_search_videos",
            description="搜索抖音视频",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "视频关键词"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_douyin_search_videos
        )
        
        self.tools["douyin_get_video_info"] = MCPTool(
            name="douyin_get_video_info",
            description="获取抖音视频信息",
            input_schema={
                "type": "object",
                "properties": {
                    "video_id": {"type": "string", "description": "视频ID"}
                },
                "required": ["video_id"]
            },
            handler=self._handle_douyin_get_video_info
        )
        
        # 快手专用工具
        self.tools["kuaishou_search_videos"] = MCPTool(
            name="kuaishou_search_videos",
            description="搜索快手视频",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "视频关键词"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_kuaishou_search_videos
        )
        
        self.tools["kuaishou_get_video_info"] = MCPTool(
            name="kuaishou_get_video_info",
            description="获取快手视频信息",
            input_schema={
                "type": "object",
                "properties": {
                    "video_id": {"type": "string", "description": "视频ID"}
                },
                "required": ["video_id"]
            },
            handler=self._handle_kuaishou_get_video_info
        )
        
        # 桌面软件集成工具
        self.tools["software_launch"] = MCPTool(
            name="software_launch",
            description="启动桌面软件",
            input_schema={
                "type": "object",
                "properties": {
                    "software_name": {"type": "string", "description": "软件名称（wps/wechat/qq）"}
                },
                "required": ["software_name"]
            },
            handler=self._handle_software_launch
        )
        
        self.tools["software_info"] = MCPTool(
            name="software_info",
            description="获取软件信息",
            input_schema={
                "type": "object",
                "properties": {
                    "software_name": {"type": "string", "description": "软件名称（wps/wechat/qq）"}
                },
                "required": ["software_name"]
            },
            handler=self._handle_software_info
        )
        
        self.tools["software_list"] = MCPTool(
            name="software_list",
            description="列出所有可用软件",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_software_list
        )
        
        # WPS Office专用工具
        self.tools["wps_open_document"] = MCPTool(
            name="wps_open_document",
            description="打开WPS文档",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "文档路径（可选）"}
                }
            },
            handler=self._handle_wps_open_document
        )
        
        self.tools["wps_create_document"] = MCPTool(
            name="wps_create_document",
            description="创建WPS文档",
            input_schema={
                "type": "object",
                "properties": {
                    "doc_type": {"type": "string", "description": "文档类型（writer/et/wpp）"}
                }
            },
            handler=self._handle_wps_create_document
        )
        
        # 微信专用工具
        self.tools["wechat_send_message"] = MCPTool(
            name="wechat_send_message",
            description="发送微信消息",
            input_schema={
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "联系人"},
                    "message": {"type": "string", "description": "消息内容"}
                }
            },
            handler=self._handle_wechat_send_message
        )
        
        self.tools["wechat_open_chat"] = MCPTool(
            name="wechat_open_chat",
            description="打开微信聊天窗口",
            input_schema={
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "联系人"}
                }
            },
            handler=self._handle_wechat_open_chat
        )
        
        # QQ专用工具
        self.tools["qq_send_message"] = MCPTool(
            name="qq_send_message",
            description="发送QQ消息",
            input_schema={
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "联系人"},
                    "message": {"type": "string", "description": "消息内容"}
                }
            },
            handler=self._handle_qq_send_message
        )
        
        self.tools["qq_open_chat"] = MCPTool(
            name="qq_open_chat",
            description="打开QQ聊天窗口",
            input_schema={
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "联系人"}
                }
            },
            handler=self._handle_qq_open_chat
        )
        
        # 凭据数据库工具
        self.tools["credential_add"] = MCPTool(
            name="credential_add",
            description="添加用户凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "用户名"},
                    "account": {"type": "string", "description": "账号"},
                    "password": {"type": "string", "description": "密码"},
                    "application": {"type": "string", "description": "应用名称"},
                    "contact": {"type": "string", "description": "联系方式"},
                    "website_url": {"type": "string", "description": "网站URL"},
                    "notes": {"type": "string", "description": "备注"}
                },
                "required": ["username", "account", "password", "application"]
            },
            handler=self._handle_credential_add
        )
        
        self.tools["credential_get"] = MCPTool(
            name="credential_get",
            description="获取用户凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "credential_id": {"type": "integer", "description": "凭据ID"}
                },
                "required": ["credential_id"]
            },
            handler=self._handle_credential_get
        )
        
        self.tools["credential_list"] = MCPTool(
            name="credential_list",
            description="获取凭据列表",
            input_schema={
                "type": "object",
                "properties": {
                    "application": {"type": "string", "description": "应用名称（可选）"},
                    "category": {"type": "string", "description": "分类（可选）"}
                }
            },
            handler=self._handle_credential_list
        )
        
        self.tools["credential_update"] = MCPTool(
            name="credential_update",
            description="更新用户凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "credential_id": {"type": "integer", "description": "凭据ID"},
                    "username": {"type": "string", "description": "用户名"},
                    "account": {"type": "string", "description": "账号"},
                    "password": {"type": "string", "description": "密码"},
                    "application": {"type": "string", "description": "应用名称"},
                    "contact": {"type": "string", "description": "联系方式"},
                    "website_url": {"type": "string", "description": "网站URL"},
                    "notes": {"type": "string", "description": "备注"}
                },
                "required": ["credential_id"]
            },
            handler=self._handle_credential_update
        )
        
        self.tools["credential_delete"] = MCPTool(
            name="credential_delete",
            description="删除用户凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "credential_id": {"type": "integer", "description": "凭据ID"}
                },
                "required": ["credential_id"]
            },
            handler=self._handle_credential_delete
        )
        
        self.tools["credential_search"] = MCPTool(
            name="credential_search",
            description="搜索用户凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["keyword"]
            },
            handler=self._handle_credential_search
        )
        
        self.tools["credential_auto_fill"] = MCPTool(
            name="credential_auto_fill",
            description="自动填充凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "application": {"type": "string", "description": "应用名称"},
                    "website_url": {"type": "string", "description": "网站URL（可选）"}
                },
                "required": ["application"]
            },
            handler=self._handle_credential_auto_fill
        )
        
        self.tools["credential_export"] = MCPTool(
            name="credential_export",
            description="导出凭据数据",
            input_schema={
                "type": "object",
                "properties": {
                    "format": {"type": "string", "description": "导出格式（json）"}
                }
            },
            handler=self._handle_credential_export
        )
        
        self.tools["credential_import"] = MCPTool(
            name="credential_import",
            description="导入凭据数据",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "导入数据"},
                    "format": {"type": "string", "description": "数据格式（json）"}
                },
                "required": ["data"]
            },
            handler=self._handle_credential_import
        )
        
        self.tools["credential_categories"] = MCPTool(
            name="credential_categories",
            description="获取应用分类列表",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_credential_categories
        )
        
        # 自动填充工具
        self.tools["auto_fill_website"] = MCPTool(
            name="auto_fill_website",
            description="为网站自动填充凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网站URL"},
                    "username_field": {"type": "string", "description": "用户名输入框标识"},
                    "password_field": {"type": "string", "description": "密码输入框标识"}
                },
                "required": ["url"]
            },
            handler=self._handle_auto_fill_website
        )
        
        self.tools["auto_fill_application"] = MCPTool(
            name="auto_fill_application",
            description="为应用自动填充凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "应用名称"},
                    "username_field": {"type": "string", "description": "用户名输入框标识"},
                    "password_field": {"type": "string", "description": "密码输入框标识"}
                },
                "required": ["app_name"]
            },
            handler=self._handle_auto_fill_application
        )
        
        self.tools["smart_auto_fill"] = MCPTool(
            name="smart_auto_fill",
            description="智能自动填充凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "标识符（URL或应用名称）"},
                    "identifier_type": {"type": "string", "description": "标识符类型（url/app/auto）"}
                },
                "required": ["identifier"]
            },
            handler=self._handle_smart_auto_fill
        )
        
        self.tools["get_suggested_credentials"] = MCPTool(
            name="get_suggested_credentials",
            description="获取建议的凭据列表",
            input_schema={
                "type": "object",
                "properties": {
                    "application": {"type": "string", "description": "应用名称"},
                    "limit": {"type": "integer", "description": "返回数量限制"}
                },
                "required": ["application"]
            },
            handler=self._handle_get_suggested_credentials
        )
        
        self.tools["validate_credential_format"] = MCPTool(
            name="validate_credential_format",
            description="验证凭据格式",
            input_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "用户名"},
                    "password": {"type": "string", "description": "密码"},
                    "application": {"type": "string", "description": "应用名称"}
                },
                "required": ["username", "password", "application"]
            },
            handler=self._handle_validate_credential_format
        )
        
        self.tools["get_auto_fill_statistics"] = MCPTool(
            name="get_auto_fill_statistics",
            description="获取自动填充统计信息",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_get_auto_fill_statistics
        )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定工具"""
        if name not in self.tools:
            return {
                "success": False,
                "error": f"工具 '{name}' 不存在",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[name]
        
        try:
            # 验证输入参数
            if not self._validate_arguments(arguments, tool.input_schema):
                return {
                    "success": False,
                    "error": "输入参数验证失败"
                }
            
            # 执行工具
            result = await tool.handler(arguments)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"工具 '{name}' 执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """简单的参数验证"""
        # 这里可以实现更复杂的JSON Schema验证
        # 目前只检查必需字段
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in arguments:
                return False
        return True
    
    # 工具处理器方法
    async def _handle_web_automate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网页自动化"""
        url = args["url"]
        steps = args.get("steps", [])
        
        result = automate_page(url=url, steps=steps, headless=False)
        return result
    
    async def _handle_bilibili_search_play(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理B站搜索播放"""
        up_name = args["up_name"]
        keep_open_seconds = args.get("keep_open_seconds", 60)
        keep_open_ms = int(keep_open_seconds * 1000)
        
        bilibili = BilibiliIntegration()
        result = bilibili.search_and_play_first_video(up_name)
        return result
    
    async def _handle_desktop_scan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理桌面文件扫描"""
        file_type = args.get("file_type", "all")
        files = self.desktop_launcher.scan_desktop_files()
        
        if file_type != "all":
            files = [f for f in files if f.get("type") == file_type]
        
        return {
            "files": files,
            "count": len(files),
            "file_type": file_type
        }
    
    async def _handle_desktop_launch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理桌面文件启动"""
        filename = args["filename"]
        exact_match = args.get("exact_match", False)
        
        result = self.desktop_launcher.launch_file(filename, exact_match=exact_match)
        return result
    
    async def _handle_web_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网络搜索"""
        query = args["query"]
        max_results = args.get("max_results", 5)
        
        results = web_search(query, max_results=max_results)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def _handle_file_read(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件读取"""
        filename = args["filename"]
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "filename": filename,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_file_write(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件写入"""
        filename = args["filename"]
        content = args["content"]
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "filename": filename,
                "size": len(content),
                "message": "文件写入成功"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_run_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理系统命令执行"""
        command = args["command"]
        timeout = args.get("timeout", 30)
        
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": "命令执行超时"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_fetch_page(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网页内容抓取"""
        url = args["url"]
        wait_selector = args.get("wait_selector")
        timeout_ms = args.get("timeout_ms", 15000)
        
        result = fetch_page(url, wait_selector, timeout_ms)
        return result
    
    async def _handle_open_website(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站打开"""
        url = args["url"]
        
        try:
            import webbrowser
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return {"message": f"已打开网站: {url}", "url": url}
        except Exception as e:
            return {"error": f"打开网站失败: {str(e)}"}
    
    async def _handle_open_bilibili(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理B站打开"""
        try:
            import webbrowser
            import time
            
            # 打开B站主页
            webbrowser.open("https://www.bilibili.com")
            time.sleep(2)
            
            # 跳转到热门视频页面
            webbrowser.open("https://www.bilibili.com/v/popular/all")
            
            return {
                "message": "已打开B站并跳转到热门视频页面",
                "url": "https://www.bilibili.com"
            }
        except Exception as e:
            return {"error": f"打开B站失败: {str(e)}"}
    
    async def _handle_play_video(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理视频播放"""
        video_url = args.get("video_url", "")
        platform = args.get("platform", "bilibili")
        query = args.get("query", "")
        
        try:
            import webbrowser
            
            if platform == "bilibili":
                if not video_url:
                    webbrowser.open("https://www.bilibili.com/v/popular/all")
                    return {
                        "message": "已打开B站热门视频页面",
                        "url": "https://www.bilibili.com/v/popular/all"
                    }
                else:
                    webbrowser.open(video_url)
                    return {
                        "message": f"已打开视频: {video_url}",
                        "url": video_url
                    }
            else:
                webbrowser.open(video_url)
                return {
                    "message": f"已打开视频: {video_url}",
                    "url": video_url
                }
        except Exception as e:
            return {"error": f"播放视频失败: {str(e)}"}
    
    async def _handle_nl_automate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理自然语言自动化"""
        query = args["query"]
        url = args.get("url", "")
        auth = args.get("auth", {})
        extra_steps = args.get("steps", [])
        
        try:
            from src.tools.executor import executor
            result = executor.action_nl_automate({
                "query": query,
                "url": url,
                "auth": auth,
                "steps": extra_steps
            })
            return result
        except Exception as e:
            return {"error": f"自然语言自动化失败: {str(e)}"}
    
    async def _handle_site_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理站点搜索"""
        url = args["url"]
        keyword = args["keyword"]
        click_first = args.get("click_first_result", True)
        
        try:
            from src.tools.executor import executor
            result = executor.site_search({
                "url": url,
                "keyword": keyword,
                "click_first_result": click_first
            })
            return result
        except Exception as e:
            return {"error": f"站点搜索失败: {str(e)}"}
    
    async def _handle_browse_product(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理商品浏览"""
        url = args["url"]
        keyword = args["keyword"]
        match_text = args.get("match_text", "")
        
        try:
            from src.tools.executor import executor
            result = executor.browse_product({
                "url": url,
                "keyword": keyword,
                "match_text": match_text
            })
            return result
        except Exception as e:
            return {"error": f"商品浏览失败: {str(e)}"}
    
    async def _handle_play_video_generic(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理通用视频播放"""
        url = args["url"]
        keyword = args["keyword"]
        match_text = args.get("match_text", "")
        
        try:
            from src.tools.executor import executor
            result = executor.play_video_generic({
                "url": url,
                "keyword": keyword,
                "match_text": match_text
            })
            return result
        except Exception as e:
            return {"error": f"通用视频播放失败: {str(e)}"}
    
    async def _handle_add_to_cart(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理加入购物车"""
        url = args["url"]
        keyword = args["keyword"]
        match_text = args.get("match_text", "")
        
        try:
            from src.tools.executor import executor
            result = executor.add_to_cart_action({
                "url": url,
                "keyword": keyword,
                "match_text": match_text
            })
            return result
        except Exception as e:
            return {"error": f"加入购物车失败: {str(e)}"}
    
    async def _handle_bilibili_open_up(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理B站UP主页打开"""
        up_name = args["up_name"]
        keep_open_seconds = args.get("keep_open_seconds", 60)
        keep_open_ms = int(keep_open_seconds * 1000)
        
        bilibili = BilibiliIntegration()
        result = bilibili.open_up_homepage(up_name)
        return result
    
    async def _handle_nl_step_execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理自然语言步骤执行"""
        instruction = args["query"]
        
        try:
            from src.tools.executor import executor
            result = executor.nl_step_execute({
                "query": instruction
            })
            return result
        except Exception as e:
            return {"error": f"步骤执行失败: {str(e)}"}
    
    async def _handle_get_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理天气查询"""
        city = args.get("city", "北京")
        
        try:
            from src.tools.executor import executor
            result = executor.get_weather({
                "city": city
            })
            return result
        except Exception as e:
            return {"error": f"获取天气失败: {str(e)}"}
    
    async def _handle_calculate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理数学计算"""
        expression = args["expression"]
        
        try:
            from src.tools.executor import executor
            result = executor.calculate({
                "expression": expression
            })
            return result
        except Exception as e:
            return {"error": f"计算失败: {str(e)}"}
    
    async def _handle_translate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理翻译"""
        text = args["text"]
        target_lang = args.get("target_lang", "en")
        
        try:
            from src.tools.executor import executor
            result = executor.translate({
                "text": text,
                "target_lang": target_lang
            })
            return result
        except Exception as e:
            return {"error": f"翻译失败: {str(e)}"}
    
    async def _handle_send_email(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理邮件发送"""
        to = args["to"]
        subject = args["subject"]
        content = args["content"]
        
        try:
            from src.tools.executor import executor
            result = executor.send_email({
                "to": to,
                "subject": subject,
                "content": content
            })
            return result
        except Exception as e:
            return {"error": f"发送邮件失败: {str(e)}"}
    
    async def _handle_schedule_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务调度"""
        task = args["task"]
        time_str = args.get("time", "")
        
        try:
            from src.tools.executor import executor
            result = executor.schedule_task({
                "task": task,
                "time": time_str
            })
            return result
        except Exception as e:
            return {"error": f"安排任务失败: {str(e)}"}
    
    # Steam集成工具处理器
    async def _handle_steam_get_library(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam游戏库获取"""
        try:
            result = steam_integration.get_game_library()
            return result
        except Exception as e:
            return {"error": f"获取Steam游戏库失败: {str(e)}"}
    
    async def _handle_steam_get_recent_activity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam最近活动获取"""
        try:
            result = steam_integration.get_recent_activity()
            return result
        except Exception as e:
            return {"error": f"获取Steam最近活动失败: {str(e)}"}
    
    async def _handle_steam_get_game_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam游戏详情获取"""
        appid = args["appid"]
        try:
            result = steam_integration.get_game_details(appid)
            return result
        except Exception as e:
            return {"error": f"获取Steam游戏详情失败: {str(e)}"}
    
    async def _handle_steam_get_friend_comparison(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam朋友比较"""
        try:
            result = steam_integration.get_friend_comparison()
            return result
        except Exception as e:
            return {"error": f"获取Steam朋友比较失败: {str(e)}"}
    
    async def _handle_steam_open_store(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam商店打开"""
        game_name = args.get("game_name", "")
        try:
            result = steam_integration.open_steam_store(game_name)
            return result
        except Exception as e:
            return {"error": f"打开Steam商店失败: {str(e)}"}
    
    async def _handle_steam_analyze_habits(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam游戏习惯分析"""
        try:
            result = steam_integration.analyze_gaming_habits()
            return result
        except Exception as e:
            return {"error": f"分析Steam游戏习惯失败: {str(e)}"}
    
    async def _handle_steam_get_recommendations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam游戏推荐"""
        try:
            result = steam_integration.get_game_recommendations()
            return result
        except Exception as e:
            return {"error": f"获取Steam游戏推荐失败: {str(e)}"}
    
    async def _handle_steam_download_game(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam游戏下载"""
        try:
            appid = args.get("appid")
            if not appid:
                return {"success": False, "error": "缺少AppID参数"}
            result = steam_integration.download_game(appid)
            return result
        except Exception as e:
            return {"error": f"下载Steam游戏失败: {str(e)}"}
    
    async def _handle_steam_uninstall_game(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam游戏卸载"""
        try:
            appid = args.get("appid")
            if not appid:
                return {"success": False, "error": "缺少AppID参数"}
            result = steam_integration.uninstall_game(appid)
            return result
        except Exception as e:
            return {"error": f"卸载Steam游戏失败: {str(e)}"}
    
    # Bilibili集成工具处理器
    async def _handle_bilibili_get_user_profile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili用户资料获取"""
        uid = args["uid"]
        try:
            result = bilibili_integration.get_user_profile(uid)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili用户资料失败: {str(e)}"}
    
    async def _handle_bilibili_search_videos(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili视频搜索"""
        keyword = args["keyword"]
        page = args.get("page", 1)
        pagesize = args.get("pagesize", 20)
        try:
            result = bilibili_integration.search_videos(keyword, page, pagesize)
            return result
        except Exception as e:
            return {"error": f"搜索Bilibili视频失败: {str(e)}"}
    
    async def _handle_bilibili_get_video_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili视频详情获取"""
        bvid = args["bvid"]
        try:
            result = bilibili_integration.get_video_details(bvid)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili视频详情失败: {str(e)}"}
    
    async def _handle_bilibili_get_user_videos(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili用户视频获取"""
        uid = args["uid"]
        page = args.get("page", 1)
        pagesize = args.get("pagesize", 20)
        try:
            result = bilibili_integration.get_user_videos(uid, page, pagesize)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili用户视频失败: {str(e)}"}
    
    async def _handle_bilibili_get_following_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili关注列表获取"""
        uid = args["uid"]
        page = args.get("page", 1)
        pagesize = args.get("pagesize", 20)
        try:
            result = bilibili_integration.get_following_list(uid, page, pagesize)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili关注列表失败: {str(e)}"}
    
    async def _handle_bilibili_get_favorites(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili收藏获取"""
        uid = args["uid"]
        page = args.get("page", 1)
        pagesize = args.get("pagesize", 20)
        try:
            result = bilibili_integration.get_user_favorites(uid, page, pagesize)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili收藏失败: {str(e)}"}
    
    async def _handle_bilibili_get_watch_later(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili稍后再看获取"""
        page = args.get("page", 1)
        pagesize = args.get("pagesize", 20)
        try:
            result = bilibili_integration.get_watch_later_list(page, pagesize)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili稍后再看失败: {str(e)}"}
    
    async def _handle_bilibili_get_user_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili用户统计获取"""
        uid = args["uid"]
        try:
            result = bilibili_integration.get_user_statistics(uid)
            return result
        except Exception as e:
            return {"error": f"获取Bilibili用户统计失败: {str(e)}"}
    
    async def _handle_bilibili_open_video(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili视频打开"""
        bvid = args["bvid"]
        try:
            result = bilibili_integration.open_bilibili_video(bvid)
            return result
        except Exception as e:
            return {"error": f"打开Bilibili视频失败: {str(e)}"}
    
    async def _handle_bilibili_open_user(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Bilibili用户主页打开"""
        uid = args["uid"]
        try:
            result = bilibili_integration.open_bilibili_user(uid)
            return result
        except Exception as e:
            return {"error": f"打开Bilibili用户主页失败: {str(e)}"}
    
    # 网站集成工具处理器
    async def _handle_website_open(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站打开"""
        url = args["url"]
        try:
            from tools.website_integration import website_integration
            result = website_integration.open_website(url)
            return result
        except Exception as e:
            return {"error": f"打开网站失败: {str(e)}"}
    
    async def _handle_website_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站搜索"""
        keyword = args["keyword"]
        website = args.get("website", "")
        try:
            from tools.website_integration import website_integration
            result = website_integration.search_website(keyword, website)
            return result
        except Exception as e:
            return {"error": f"网站搜索失败: {str(e)}"}
    
    async def _handle_website_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站信息总结"""
        url = args["url"]
        try:
            from tools.website_integration import website_integration
            result = website_integration.get_website_summary(url)
            return result
        except Exception as e:
            return {"error": f"获取网站总结失败: {str(e)}"}
    
    # 京东专用工具处理器
    async def _handle_jd_search_products(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理京东商品搜索"""
        keyword = args["keyword"]
        page = args.get("page", 1)
        try:
            from tools.website_integration import jd_integration
            result = jd_integration.search_products(keyword, page)
            return result
        except Exception as e:
            return {"error": f"京东商品搜索失败: {str(e)}"}
    
    async def _handle_jd_get_product_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理京东商品信息获取"""
        product_id = args["product_id"]
        try:
            from tools.website_integration import jd_integration
            result = jd_integration.get_product_info(product_id)
            return result
        except Exception as e:
            return {"error": f"获取京东商品信息失败: {str(e)}"}
    
    # 淘宝专用工具处理器
    async def _handle_taobao_search_products(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理淘宝商品搜索"""
        keyword = args["keyword"]
        page = args.get("page", 1)
        try:
            from tools.website_integration import taobao_integration
            result = taobao_integration.search_products(keyword, page)
            return result
        except Exception as e:
            return {"error": f"淘宝商品搜索失败: {str(e)}"}
    
    async def _handle_taobao_get_product_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理淘宝商品信息获取"""
        product_id = args["product_id"]
        try:
            from tools.website_integration import taobao_integration
            result = taobao_integration.get_product_info(product_id)
            return result
        except Exception as e:
            return {"error": f"获取淘宝商品信息失败: {str(e)}"}
    
    # 高德地图专用工具处理器
    async def _handle_amap_search_location(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理高德地图位置搜索"""
        keyword = args["keyword"]
        try:
            from tools.website_integration import amap_integration
            result = amap_integration.search_location(keyword)
            return result
        except Exception as e:
            return {"error": f"高德地图搜索失败: {str(e)}"}
    
    async def _handle_amap_get_route(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理高德地图路线获取"""
        start = args["start"]
        end = args["end"]
        mode = args.get("mode", "driving")
        try:
            from tools.website_integration import amap_integration
            result = amap_integration.get_route(start, end, mode)
            return result
        except Exception as e:
            return {"error": f"获取高德地图路线失败: {str(e)}"}
    
    # 拼多多专用工具处理器
    async def _handle_pdd_search_products(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理拼多多商品搜索"""
        keyword = args["keyword"]
        page = args.get("page", 1)
        try:
            from tools.website_integration import pinduoduo_integration
            result = pinduoduo_integration.search_products(keyword, page)
            return result
        except Exception as e:
            return {"error": f"拼多多商品搜索失败: {str(e)}"}
    
    async def _handle_pdd_get_product_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理拼多多商品信息获取"""
        product_id = args["product_id"]
        try:
            from tools.website_integration import pinduoduo_integration
            result = pinduoduo_integration.get_product_info(product_id)
            return result
        except Exception as e:
            return {"error": f"获取拼多多商品信息失败: {str(e)}"}
    
    # 抖音专用工具处理器
    async def _handle_douyin_search_videos(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理抖音视频搜索"""
        keyword = args["keyword"]
        try:
            from tools.website_integration import douyin_integration
            result = douyin_integration.search_videos(keyword)
            return result
        except Exception as e:
            return {"error": f"抖音视频搜索失败: {str(e)}"}
    
    async def _handle_douyin_get_video_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理抖音视频信息获取"""
        video_id = args["video_id"]
        try:
            from tools.website_integration import douyin_integration
            result = douyin_integration.get_video_info(video_id)
            return result
        except Exception as e:
            return {"error": f"获取抖音视频信息失败: {str(e)}"}
    
    # 快手专用工具处理器
    async def _handle_kuaishou_search_videos(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理快手视频搜索"""
        keyword = args["keyword"]
        try:
            from tools.website_integration import kuaishou_integration
            result = kuaishou_integration.search_videos(keyword)
            return result
        except Exception as e:
            return {"error": f"快手视频搜索失败: {str(e)}"}
    
    async def _handle_kuaishou_get_video_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理快手视频信息获取"""
        video_id = args["video_id"]
        try:
            from tools.website_integration import kuaishou_integration
            result = kuaishou_integration.get_video_info(video_id)
            return result
        except Exception as e:
            return {"error": f"获取快手视频信息失败: {str(e)}"}
    
    # 桌面软件集成工具处理器
    async def _handle_software_launch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理桌面软件启动"""
        software_name = args["software_name"]
        try:
            from tools.desktop_software_integration import desktop_software_integration
            result = desktop_software_integration.launch_software(software_name)
            return result
        except Exception as e:
            return {"error": f"启动软件失败: {str(e)}"}
    
    async def _handle_software_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理软件信息获取"""
        software_name = args["software_name"]
        try:
            from tools.desktop_software_integration import desktop_software_integration
            result = desktop_software_integration.get_software_info(software_name)
            return result
        except Exception as e:
            return {"error": f"获取软件信息失败: {str(e)}"}
    
    async def _handle_software_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理软件列表获取"""
        try:
            from tools.desktop_software_integration import desktop_software_integration
            result = desktop_software_integration.list_available_software()
            return result
        except Exception as e:
            return {"error": f"获取软件列表失败: {str(e)}"}
    
    # WPS Office专用工具处理器
    async def _handle_wps_open_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理WPS文档打开"""
        file_path = args.get("file_path", "")
        try:
            from tools.desktop_software_integration import wps_integration
            result = wps_integration.open_document(file_path)
            return result
        except Exception as e:
            return {"error": f"打开WPS文档失败: {str(e)}"}
    
    async def _handle_wps_create_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理WPS文档创建"""
        doc_type = args.get("doc_type", "writer")
        try:
            from tools.desktop_software_integration import wps_integration
            result = wps_integration.create_document(doc_type)
            return result
        except Exception as e:
            return {"error": f"创建WPS文档失败: {str(e)}"}
    
    # 微信专用工具处理器
    async def _handle_wechat_send_message(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理微信消息发送"""
        contact = args.get("contact", "")
        message = args.get("message", "")
        try:
            from tools.desktop_software_integration import wechat_integration
            result = wechat_integration.send_message(contact, message)
            return result
        except Exception as e:
            return {"error": f"发送微信消息失败: {str(e)}"}
    
    async def _handle_wechat_open_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理微信聊天窗口打开"""
        contact = args.get("contact", "")
        try:
            from tools.desktop_software_integration import wechat_integration
            result = wechat_integration.open_chat(contact)
            return result
        except Exception as e:
            return {"error": f"打开微信聊天失败: {str(e)}"}
    
    # QQ专用工具处理器
    async def _handle_qq_send_message(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理QQ消息发送"""
        contact = args.get("contact", "")
        message = args.get("message", "")
        try:
            from tools.desktop_software_integration import qq_integration
            result = qq_integration.send_message(contact, message)
            return result
        except Exception as e:
            return {"error": f"发送QQ消息失败: {str(e)}"}
    
    async def _handle_qq_open_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理QQ聊天窗口打开"""
        contact = args.get("contact", "")
        try:
            from tools.desktop_software_integration import qq_integration
            result = qq_integration.open_chat(contact)
            return result
        except Exception as e:
            return {"error": f"打开QQ聊天失败: {str(e)}"}
    
    # 凭据数据库工具处理器
    async def _handle_credential_add(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据添加"""
        try:
            from database.credential_db import credential_db
            result = credential_db.add_credential(**args)
            return result
        except Exception as e:
            return {"error": f"添加凭据失败: {str(e)}"}
    
    async def _handle_credential_get(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据获取"""
        credential_id = args["credential_id"]
        try:
            from database.credential_db import credential_db
            result = credential_db.get_credential(credential_id)
            return result
        except Exception as e:
            return {"error": f"获取凭据失败: {str(e)}"}
    
    async def _handle_credential_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据列表获取"""
        application = args.get("application")
        category = args.get("category")
        try:
            from database.credential_db import credential_db
            if application:
                result = credential_db.get_credentials_by_application(application)
            else:
                result = credential_db.get_all_credentials(category)
            return result
        except Exception as e:
            return {"error": f"获取凭据列表失败: {str(e)}"}
    
    async def _handle_credential_update(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据更新"""
        credential_id = args["credential_id"]
        update_data = {k: v for k, v in args.items() if k != "credential_id"}
        try:
            from database.credential_db import credential_db
            result = credential_db.update_credential(credential_id, **update_data)
            return result
        except Exception as e:
            return {"error": f"更新凭据失败: {str(e)}"}
    
    async def _handle_credential_delete(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据删除"""
        credential_id = args["credential_id"]
        try:
            from database.credential_db import credential_db
            result = credential_db.delete_credential(credential_id)
            return result
        except Exception as e:
            return {"error": f"删除凭据失败: {str(e)}"}
    
    async def _handle_credential_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据搜索"""
        keyword = args["keyword"]
        try:
            from database.credential_db import credential_db
            result = credential_db.search_credentials(keyword)
            return result
        except Exception as e:
            return {"error": f"搜索凭据失败: {str(e)}"}
    
    async def _handle_credential_auto_fill(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据自动填充"""
        application = args["application"]
        website_url = args.get("website_url", "")
        try:
            from database.credential_db import credential_db
            result = credential_db.auto_fill_credential(application, website_url)
            return result
        except Exception as e:
            return {"error": f"自动填充凭据失败: {str(e)}"}
    
    async def _handle_credential_export(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据导出"""
        format_type = args.get("format", "json")
        try:
            from database.credential_db import credential_db
            result = credential_db.export_credentials(format_type)
            return result
        except Exception as e:
            return {"error": f"导出凭据失败: {str(e)}"}
    
    async def _handle_credential_import(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据导入"""
        data = args["data"]
        format_type = args.get("format", "json")
        try:
            from database.credential_db import credential_db
            result = credential_db.import_credentials(data, format_type)
            return result
        except Exception as e:
            return {"error": f"导入凭据失败: {str(e)}"}
    
    async def _handle_credential_categories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理应用分类获取"""
        try:
            from database.credential_db import credential_db
            result = credential_db.get_application_categories()
            return result
        except Exception as e:
            return {"error": f"获取应用分类失败: {str(e)}"}
    
    # 自动填充工具处理器
    async def _handle_auto_fill_website(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站自动填充"""
        url = args["url"]
        username_field = args.get("username_field", "")
        password_field = args.get("password_field", "")
        try:
            from tools.auto_fill_integration import auto_fill_integration
            result = auto_fill_integration.auto_fill_for_website(url, username_field, password_field)
            return result
        except Exception as e:
            return {"error": f"网站自动填充失败: {str(e)}"}
    
    async def _handle_auto_fill_application(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理应用自动填充"""
        app_name = args["app_name"]
        username_field = args.get("username_field", "")
        password_field = args.get("password_field", "")
        try:
            from tools.auto_fill_integration import auto_fill_integration
            result = auto_fill_integration.auto_fill_for_application(app_name, username_field, password_field)
            return result
        except Exception as e:
            return {"error": f"应用自动填充失败: {str(e)}"}
    
    async def _handle_smart_auto_fill(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理智能自动填充"""
        identifier = args["identifier"]
        identifier_type = args.get("identifier_type", "auto")
        try:
            from tools.auto_fill_integration import auto_fill_integration
            result = auto_fill_integration.smart_auto_fill(identifier, identifier_type)
            return result
        except Exception as e:
            return {"error": f"智能自动填充失败: {str(e)}"}
    
    async def _handle_get_suggested_credentials(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理获取建议凭据"""
        application = args["application"]
        limit = args.get("limit", 5)
        try:
            from tools.auto_fill_integration import auto_fill_integration
            result = auto_fill_integration.get_suggested_credentials(application, limit)
            return result
        except Exception as e:
            return {"error": f"获取建议凭据失败: {str(e)}"}
    
    async def _handle_validate_credential_format(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证凭据格式"""
        username = args["username"]
        password = args["password"]
        application = args["application"]
        try:
            from tools.auto_fill_integration import auto_fill_integration
            result = auto_fill_integration.validate_credential_format(username, password, application)
            return result
        except Exception as e:
            return {"error": f"验证凭据格式失败: {str(e)}"}
    
    async def _handle_get_auto_fill_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理获取自动填充统计"""
        try:
            from tools.auto_fill_integration import auto_fill_integration
            result = auto_fill_integration.get_auto_fill_statistics()
            return result
        except Exception as e:
            return {"error": f"获取自动填充统计失败: {str(e)}"}
    
    def _register_auto_login_tools(self):
        """注册自动登录工具"""
        
        # 网站自动登录工具
        self.tools["website_auto_login"] = MCPTool(
            name="website_auto_login",
            description="为指定网站执行自动登录操作",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标网站URL"}
                },
                "required": ["url"]
            },
            handler=self._handle_website_auto_login
        )
        
        # 网站登录状态检查工具
        self.tools["check_login_status"] = MCPTool(
            name="check_login_status",
            description="检查网站是否需要登录以及是否有对应凭据",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标网站URL"}
                },
                "required": ["url"]
            },
            handler=self._handle_check_login_status
        )
    
    async def _handle_website_auto_login(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站自动登录"""
        try:
            from src.mcp.handlers.auto_login_handler import AutoLoginHandler
            handler = AutoLoginHandler()
            return await handler.handle(args)
        except Exception as e:
            return {"error": f"网站自动登录失败: {str(e)}"}
    
    async def _handle_check_login_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理登录状态检查"""
        try:
            from src.mcp.handlers.auto_login_handler import WebsiteLoginHandler
            handler = WebsiteLoginHandler()
            return await handler.handle(args)
        except Exception as e:
            return {"error": f"登录状态检查失败: {str(e)}"}

# 全局MCP服务器实例
mcp_server = LAMMCPServer()

async def main():
    """MCP服务器主函数"""
    print("LAM-Agent MCP服务器启动中...")
    
    # 列出所有工具
    tools = await mcp_server.list_tools()
    print(f"已注册 {len(tools)} 个工具:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # 这里可以添加MCP协议的stdin/stdout通信逻辑
    # 目前只是演示工具注册和调用

if __name__ == "__main__":
    asyncio.run(main())
