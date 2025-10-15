#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP工具注册器
"""

import logging
from typing import Dict, Any, List
from ..core.base import BaseToolRegistry, MCPTool
from ..handlers.web_handler import WebAutomationHandler, WebSearchHandler, PageFetchHandler
from ..handlers.bilibili_handler import BilibiliSearchPlayHandler, BilibiliOpenUpHandler, BilibiliIntegrationHandler
from ..handlers.steam_handler import SteamIntegrationHandler
from ..handlers.desktop_handler import DesktopScanHandler, DesktopLaunchHandler, DesktopSoftwareHandler
from ..handlers.website_handler import WebsiteIntegrationHandler
from ..handlers.credential_handler import CredentialDatabaseHandler, AutoFillHandler
from ..handlers.general_handler import (
    NLStepExecuteHandler, NLAutomateHandler, CalculatorHandler, 
    WeatherHandler, TranslateHandler, EmailHandler, TaskScheduleHandler
)

logger = logging.getLogger(__name__)

class LAMToolRegistry(BaseToolRegistry):
    """LAM-Agent工具注册器"""
    
    def __init__(self):
        super().__init__()
        self._initialize_handlers()
        self.register_tools()
    
    def _initialize_handlers(self):
        """初始化处理器"""
        self.handlers = {
            # 网页处理器
            'web_automation': WebAutomationHandler(),
            'web_search': WebSearchHandler(),
            'page_fetch': PageFetchHandler(),
            
            # B站处理器
            'bilibili_search_play': BilibiliSearchPlayHandler(),
            'bilibili_open_up': BilibiliOpenUpHandler(),
            'bilibili_integration': BilibiliIntegrationHandler(),
            
            # Steam处理器
            'steam_integration': SteamIntegrationHandler(),
            
            # 桌面处理器
            'desktop_scan': DesktopScanHandler(),
            'desktop_launch': DesktopLaunchHandler(),
            'desktop_software': DesktopSoftwareHandler(),
            
            # 网站处理器
            'website_integration': WebsiteIntegrationHandler(),
            
            # 凭据处理器
            'credential_database': CredentialDatabaseHandler(),
            'auto_fill': AutoFillHandler(),
            
            # 通用处理器
            'nl_step_execute': NLStepExecuteHandler(),
            'nl_automate': NLAutomateHandler(),
            'calculator': CalculatorHandler(),
            'weather': WeatherHandler(),
            'translate': TranslateHandler(),
            'email': EmailHandler(),
            'task_schedule': TaskScheduleHandler(),
        }
    
    def register_tools(self):
        """注册所有工具"""
        # 网页自动化工具
        self.register_tool(MCPTool(
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
            handler=self.handlers['web_automation'].handle
        ))
        
        # B站搜索播放工具
        self.register_tool(MCPTool(
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
            handler=self.handlers['bilibili_search_play'].handle
        ))
        
        # 桌面文件管理工具
        self.register_tool(MCPTool(
            name="desktop_scan",
            description="扫描桌面文件和快捷方式",
            input_schema={
                "type": "object",
                "properties": {
                    "file_type": {"type": "string", "description": "文件类型过滤", "default": "all"}
                }
            },
            handler=self.handlers['desktop_scan'].handle
        ))
        
        # 桌面文件启动工具
        self.register_tool(MCPTool(
            name="desktop_launch",
            description="启动桌面文件或应用程序",
            input_schema={
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "要启动的文件名"}
                },
                "required": ["file_name"]
            },
            handler=self.handlers['desktop_launch'].handle
        ))
        
        # 网页搜索工具
        self.register_tool(MCPTool(
            name="web_search",
            description="在网页上搜索信息",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "max_results": {"type": "integer", "description": "最大结果数量", "default": 10}
                },
                "required": ["query"]
            },
            handler=self.handlers['web_search'].handle
        ))
        
        # 页面获取工具
        self.register_tool(MCPTool(
            name="page_fetch",
            description="获取网页内容",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标网页URL"}
                },
                "required": ["url"]
            },
            handler=self.handlers['page_fetch'].handle
        ))
        
        # B站打开UP主页面工具
        self.register_tool(MCPTool(
            name="bilibili_open_up",
            description="打开B站UP主主页",
            input_schema={
                "type": "object",
                "properties": {
                    "up_name": {"type": "string", "description": "UP主名称"}
                },
                "required": ["up_name"]
            },
            handler=self.handlers['bilibili_open_up'].handle
        ))
        
        # 自然语言自动化工具
        self.register_tool(MCPTool(
            name="nl_automate",
            description="使用自然语言描述执行自动化操作",
            input_schema={
                "type": "object",
                "properties": {
                    "instruction": {"type": "string", "description": "自然语言指令"}
                },
                "required": ["instruction"]
            },
            handler=self.handlers['nl_automate'].handle
        ))
        
        # 网站搜索工具
        self.register_tool(MCPTool(
            name="site_search",
            description="在指定网站内搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标网站URL"},
                    "keyword": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["url", "keyword"]
            },
            handler=self.handlers['website_integration'].handle
        ))
        
        # 商品浏览工具
        self.register_tool(MCPTool(
            name="browse_product",
            description="浏览商品信息",
            input_schema={
                "type": "object",
                "properties": {
                    "product_url": {"type": "string", "description": "商品页面URL"}
                },
                "required": ["product_url"]
            },
            handler=self.handlers['website_integration'].handle
        ))
        
        # 通用视频播放工具
        self.register_tool(MCPTool(
            name="play_video_generic",
            description="播放通用视频",
            input_schema={
                "type": "object",
                "properties": {
                    "video_url": {"type": "string", "description": "视频URL"}
                },
                "required": ["video_url"]
            },
            handler=self.handlers['website_integration'].handle
        ))
        
        # 添加到购物车工具
        self.register_tool(MCPTool(
            name="add_to_cart",
            description="将商品添加到购物车",
            input_schema={
                "type": "object",
                "properties": {
                    "product_url": {"type": "string", "description": "商品页面URL"}
                },
                "required": ["product_url"]
            },
            handler=self.handlers['website_integration'].handle
        ))
        
        # 自然语言步骤执行工具
        self.register_tool(MCPTool(
            name="nl_step_execute",
            description="执行自然语言描述的步骤",
            input_schema={
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "description": "步骤列表",
                        "items": {"type": "string"}
                    }
                },
                "required": ["steps"]
            },
            handler=self.handlers['nl_step_execute'].handle
        ))
        
        # 天气查询工具
        self.register_tool(MCPTool(
            name="get_weather",
            description="获取天气信息",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            },
            handler=self.handlers['weather'].handle
        ))
        
        # 计算器工具
        self.register_tool(MCPTool(
            name="calculate",
            description="执行数学计算",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            },
            handler=self.handlers['calculator'].handle
        ))
        
        # 翻译工具
        self.register_tool(MCPTool(
            name="translate",
            description="翻译文本",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要翻译的文本"},
                    "target_lang": {"type": "string", "description": "目标语言", "default": "en"},
                    "source_lang": {"type": "string", "description": "源语言", "default": "auto"}
                },
                "required": ["text"]
            },
            handler=self.handlers['translate'].handle
        ))
        
        # 邮件发送工具
        self.register_tool(MCPTool(
            name="send_email",
            description="发送邮件",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "收件人邮箱"},
                    "subject": {"type": "string", "description": "邮件主题"},
                    "body": {"type": "string", "description": "邮件内容"}
                },
                "required": ["to", "subject", "body"]
            },
            handler=self.handlers['email'].handle
        ))
        
        # 任务调度工具
        self.register_tool(MCPTool(
            name="schedule_task",
            description="调度任务",
            input_schema={
                "type": "object",
                "properties": {
                    "task_name": {"type": "string", "description": "任务名称"},
                    "schedule_time": {"type": "string", "description": "调度时间"},
                    "task_data": {"type": "object", "description": "任务数据", "default": {}}
                },
                "required": ["task_name", "schedule_time"]
            },
            handler=self.handlers['task_schedule'].handle
        ))
        
        # Steam工具
        self._register_steam_tools()
        
        # Bilibili集成工具
        self._register_bilibili_tools()
        
        # 网站集成工具
        self._register_website_tools()
        
        # 桌面软件工具
        self._register_desktop_software_tools()
        
        # 凭据管理工具
        self._register_credential_tools()
        
        # 自动填充工具
        self._register_auto_fill_tools()
    
    def _register_steam_tools(self):
        """注册Steam工具"""
        steam_tools = [
            ("steam_get_library", "获取Steam游戏库", {"type": "object", "properties": {}, "required": []}),
            ("steam_get_recent_activity", "获取Steam最近活动", {"type": "object", "properties": {}, "required": []}),
            ("steam_get_game_details", "获取游戏详情", {"type": "object", "properties": {"appid": {"type": "string"}}, "required": ["appid"]}),
            ("steam_get_friend_comparison", "获取朋友比较", {"type": "object", "properties": {}, "required": []}),
            ("steam_open_store", "打开Steam商店", {"type": "object", "properties": {}, "required": []}),
            ("steam_analyze_habits", "分析游戏习惯", {"type": "object", "properties": {}, "required": []}),
            ("steam_get_recommendations", "获取游戏推荐", {"type": "object", "properties": {}, "required": []}),
            ("steam_download_game", "下载游戏", {"type": "object", "properties": {"appid": {"type": "string"}}, "required": ["appid"]}),
            ("steam_uninstall_game", "卸载游戏", {"type": "object", "properties": {"appid": {"type": "string"}}, "required": ["appid"]})
        ]
        
        for name, description, schema in steam_tools:
            self.register_tool(MCPTool(
                name=name,
                description=description,
                input_schema=schema,
                handler=self.handlers['steam_integration'].handle
            ))
    
    def _register_bilibili_tools(self):
        """注册Bilibili工具"""
        bilibili_tools = [
            ("bilibili_get_user_profile", "获取用户资料", {"type": "object", "properties": {"uid": {"type": "string"}}, "required": ["uid"]}),
            ("bilibili_search_videos", "搜索视频", {"type": "object", "properties": {"keyword": {"type": "string"}, "page": {"type": "integer", "default": 1}}, "required": ["keyword"]}),
            ("bilibili_get_video_details", "获取视频详情", {"type": "object", "properties": {"bvid": {"type": "string"}}, "required": ["bvid"]}),
            ("bilibili_get_user_videos", "获取用户视频", {"type": "object", "properties": {"uid": {"type": "string"}, "page": {"type": "integer", "default": 1}}, "required": ["uid"]}),
            ("bilibili_get_following_list", "获取关注列表", {"type": "object", "properties": {"uid": {"type": "string"}, "page": {"type": "integer", "default": 1}}, "required": ["uid"]}),
            ("bilibili_get_favorites", "获取收藏", {"type": "object", "properties": {"uid": {"type": "string"}, "page": {"type": "integer", "default": 1}}, "required": ["uid"]}),
            ("bilibili_get_watch_later", "获取稍后再看", {"type": "object", "properties": {"uid": {"type": "string"}, "page": {"type": "integer", "default": 1}}, "required": ["uid"]}),
            ("bilibili_get_user_statistics", "获取用户统计", {"type": "object", "properties": {"uid": {"type": "string"}}, "required": ["uid"]}),
            ("bilibili_open_video", "打开视频", {"type": "object", "properties": {"bvid": {"type": "string"}}, "required": ["bvid"]}),
            ("bilibili_open_user", "打开用户", {"type": "object", "properties": {"uid": {"type": "string"}}, "required": ["uid"]})
        ]
        
        for name, description, schema in bilibili_tools:
            self.register_tool(MCPTool(
                name=name,
                description=description,
                input_schema=schema,
                handler=self.handlers['bilibili_integration'].handle
            ))
    
    def _register_website_tools(self):
        """注册网站工具"""
        website_tools = [
            ("website_open", "打开网站", {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}),
            ("website_search", "搜索网站", {"type": "object", "properties": {"url": {"type": "string"}, "keyword": {"type": "string"}}, "required": ["url", "keyword"]}),
            ("website_summary", "网站摘要", {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}),
            ("jd_search_products", "京东搜索商品", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("jd_get_product_info", "获取京东商品信息", {"type": "object", "properties": {"product_id": {"type": "string"}}, "required": ["product_id"]}),
            ("taobao_search_products", "淘宝搜索商品", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("taobao_get_product_info", "获取淘宝商品信息", {"type": "object", "properties": {"product_id": {"type": "string"}}, "required": ["product_id"]}),
            ("amap_search_location", "高德搜索地点", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("amap_get_route", "高德获取路线", {"type": "object", "properties": {"start": {"type": "string"}, "end": {"type": "string"}}, "required": ["start", "end"]}),
            ("pdd_search_products", "拼多多搜索商品", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("pdd_get_product_info", "获取拼多多商品信息", {"type": "object", "properties": {"product_id": {"type": "string"}}, "required": ["product_id"]}),
            ("douyin_search_videos", "抖音搜索视频", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("douyin_get_video_info", "获取抖音视频信息", {"type": "object", "properties": {"video_id": {"type": "string"}}, "required": ["video_id"]}),
            ("kuaishou_search_videos", "快手搜索视频", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("kuaishou_get_video_info", "获取快手视频信息", {"type": "object", "properties": {"video_id": {"type": "string"}}, "required": ["video_id"]})
        ]
        
        for name, description, schema in website_tools:
            self.register_tool(MCPTool(
                name=name,
                description=description,
                input_schema=schema,
                handler=self.handlers['website_integration'].handle
            ))
    
    def _register_desktop_software_tools(self):
        """注册桌面软件工具"""
        software_tools = [
            ("software_launch", "启动软件", {"type": "object", "properties": {"software_name": {"type": "string"}}, "required": ["software_name"]}),
            ("software_info", "获取软件信息", {"type": "object", "properties": {"software_name": {"type": "string"}}, "required": ["software_name"]}),
            ("software_list", "列出软件", {"type": "object", "properties": {}, "required": []}),
            ("wps_open_document", "WPS打开文档", {"type": "object", "properties": {"document_path": {"type": "string"}}, "required": ["document_path"]}),
            ("wps_create_document", "WPS创建文档", {"type": "object", "properties": {"document_name": {"type": "string"}}, "required": ["document_name"]}),
            ("wechat_send_message", "微信发送消息", {"type": "object", "properties": {"contact": {"type": "string"}, "message": {"type": "string"}}, "required": ["contact", "message"]}),
            ("wechat_open_chat", "微信打开聊天", {"type": "object", "properties": {"contact": {"type": "string"}}, "required": ["contact"]}),
            ("qq_send_message", "QQ发送消息", {"type": "object", "properties": {"contact": {"type": "string"}, "message": {"type": "string"}}, "required": ["contact", "message"]}),
            ("qq_open_chat", "QQ打开聊天", {"type": "object", "properties": {"contact": {"type": "string"}}, "required": ["contact"]})
        ]
        
        for name, description, schema in software_tools:
            self.register_tool(MCPTool(
                name=name,
                description=description,
                input_schema=schema,
                handler=self.handlers['desktop_software'].handle
            ))
    
    def _register_credential_tools(self):
        """注册凭据管理工具"""
        credential_tools = [
            ("credential_add", "添加凭据", {"type": "object", "properties": {"username": {"type": "string"}, "account": {"type": "string"}, "password": {"type": "string"}, "application": {"type": "string"}, "contact": {"type": "string", "default": ""}, "website_url": {"type": "string", "default": ""}, "notes": {"type": "string", "default": ""}}, "required": ["username", "account", "password", "application"]}),
            ("credential_get", "获取凭据", {"type": "object", "properties": {"credential_id": {"type": "integer"}}, "required": ["credential_id"]}),
            ("credential_list", "列出凭据", {"type": "object", "properties": {"category": {"type": "string", "default": None}}, "required": []}),
            ("credential_update", "更新凭据", {"type": "object", "properties": {"credential_id": {"type": "integer"}, "username": {"type": "string"}, "account": {"type": "string"}, "password": {"type": "string"}, "application": {"type": "string"}, "contact": {"type": "string"}, "website_url": {"type": "string"}, "notes": {"type": "string"}}, "required": ["credential_id"]}),
            ("credential_delete", "删除凭据", {"type": "object", "properties": {"credential_id": {"type": "integer"}}, "required": ["credential_id"]}),
            ("credential_search", "搜索凭据", {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
            ("credential_auto_fill", "自动填充凭据", {"type": "object", "properties": {"application": {"type": "string"}, "website_url": {"type": "string", "default": ""}}, "required": ["application"]}),
            ("credential_export", "导出凭据", {"type": "object", "properties": {"file_path": {"type": "string", "default": "credentials_export.json"}}, "required": []}),
            ("credential_import", "导入凭据", {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
            ("credential_categories", "获取分类", {"type": "object", "properties": {}, "required": []})
        ]
        
        for name, description, schema in credential_tools:
            self.register_tool(MCPTool(
                name=name,
                description=description,
                input_schema=schema,
                handler=self.handlers['credential_database'].handle
            ))
    
    def _register_auto_fill_tools(self):
        """注册自动填充工具"""
        auto_fill_tools = [
            ("auto_fill_website", "网站自动填充", {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}),
            ("auto_fill_application", "应用自动填充", {"type": "object", "properties": {"application": {"type": "string"}}, "required": ["application"]}),
            ("smart_auto_fill", "智能自动填充", {"type": "object", "properties": {"identifier": {"type": "string"}, "identifier_type": {"type": "string", "default": "auto"}}, "required": ["identifier"]}),
            ("get_suggested_credentials", "获取建议凭据", {"type": "object", "properties": {"application": {"type": "string"}, "limit": {"type": "integer", "default": 5}}, "required": ["application"]}),
            ("validate_credential_format", "验证凭据格式", {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}, "application": {"type": "string"}}, "required": ["username", "password", "application"]}),
            ("get_auto_fill_statistics", "获取自动填充统计", {"type": "object", "properties": {}, "required": []})
        ]
        
        for name, description, schema in auto_fill_tools:
            self.register_tool(MCPTool(
                name=name,
                description=description,
                input_schema=schema,
                handler=self.handlers['auto_fill'].handle
            ))
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """按类别获取工具"""
        return {
            "网页自动化": ["web_automate", "web_search", "page_fetch", "site_search", "browse_product", "play_video_generic", "add_to_cart"],
            "B站操作": ["bilibili_search_play", "bilibili_open_up", "bilibili_get_user_profile", "bilibili_search_videos", "bilibili_get_video_details", "bilibili_get_user_videos", "bilibili_get_following_list", "bilibili_get_favorites", "bilibili_get_watch_later", "bilibili_get_user_statistics", "bilibili_open_video", "bilibili_open_user"],
            "桌面管理": ["desktop_scan", "desktop_launch", "software_launch", "software_info", "software_list", "wps_open_document", "wps_create_document", "wechat_send_message", "wechat_open_chat", "qq_send_message", "qq_open_chat"],
            "Steam集成": ["steam_get_library", "steam_get_recent_activity", "steam_get_game_details", "steam_get_friend_comparison", "steam_open_store", "steam_analyze_habits", "steam_get_recommendations", "steam_download_game", "steam_uninstall_game"],
            "网站集成": ["website_open", "website_search", "website_summary", "jd_search_products", "jd_get_product_info", "taobao_search_products", "taobao_get_product_info", "amap_search_location", "amap_get_route", "pdd_search_products", "pdd_get_product_info", "douyin_search_videos", "douyin_get_video_info", "kuaishou_search_videos", "kuaishou_get_video_info"],
            "凭据管理": ["credential_add", "credential_get", "credential_list", "credential_update", "credential_delete", "credential_search", "credential_auto_fill", "credential_export", "credential_import", "credential_categories"],
            "自动填充": ["auto_fill_website", "auto_fill_application", "smart_auto_fill", "get_suggested_credentials", "validate_credential_format", "get_auto_fill_statistics"],
            "通用工具": ["nl_step_execute", "nl_automate", "get_weather", "calculate", "translate", "send_email", "schedule_task"]
        }


