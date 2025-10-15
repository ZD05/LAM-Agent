#!/usr/bin/env python3
"""
LAM-Agent MCP客户端实现
用于LamAgent与MCP服务器通信
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import subprocess
import sys
import os

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP客户端，用于与MCP服务器通信"""
    
    def __init__(self, server_command: Optional[str] = None):
        self.server_command = server_command or [sys.executable, "-m", "src.mcp.server"]
        self.process: Optional[subprocess.Popen] = None
        self.tools_cache: List[Dict[str, Any]] = []
    
    async def start_server(self):
        """启动MCP服务器进程"""
        try:
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                bufsize=0
            )
            logger.info("MCP服务器已启动")
            
            # 初始化连接
            await self._initialize()
            
        except Exception as e:
            logger.error(f"启动MCP服务器失败: {e}")
            raise
    
    async def stop_server(self):
        """停止MCP服务器进程"""
        if self.process:
            self.process.terminate()
            await asyncio.sleep(1)
            if self.process.poll() is None:
                self.process.kill()
            self.process = None
            logger.info("MCP服务器已停止")
    
    async def _initialize(self):
        """初始化MCP连接"""
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "lam-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        await self._send_request(init_request)
        
        # 获取工具列表
        await self.list_tools()
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到MCP服务器"""
        if not self.process:
            raise RuntimeError("MCP服务器未启动")
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # 读取响应
        response_str = self.process.stdout.readline()
        if not response_str:
            raise RuntimeError("MCP服务器无响应")
        
        try:
            response = json.loads(response_str.strip())
            return response
        except json.JSONDecodeError as e:
            logger.error(f"解析MCP响应失败: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await self._send_request(request)
        
        if "result" in response and "tools" in response["result"]:
            self.tools_cache = response["result"]["tools"]
            return self.tools_cache
        else:
            logger.error(f"获取工具列表失败: {response}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "result" in response:
            return response["result"]
        else:
            error = response.get("error", {})
            return {
                "success": False,
                "error": error.get("message", "未知错误")
            }
    
    def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取工具信息"""
        for tool in self.tools_cache:
            if tool["name"] == name:
                return tool
        return None
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """根据类别获取工具列表"""
        # 这里可以根据工具名称或描述进行分类
        category_keywords = {
            "web": ["web_automate", "fetch_page", "web_search", "open_website", "site_search", "browse_product", "play_video_generic", "add_to_cart"],
            "bilibili": ["bilibili_search_play", "bilibili_open_up", "bilibili_get_user_profile", "bilibili_search_videos", "bilibili_get_video_details", "bilibili_get_user_videos", "bilibili_get_following_list", "bilibili_get_favorites", "bilibili_get_watch_later", "bilibili_get_user_statistics", "bilibili_open_video", "bilibili_open_user"],
            "website": ["website_open", "website_search", "website_summary"],
            "jd": ["jd_search_products", "jd_get_product_info"],
            "taobao": ["taobao_search_products", "taobao_get_product_info"],
            "amap": ["amap_search_location", "amap_get_route"],
            "pdd": ["pdd_search_products", "pdd_get_product_info"],
            "douyin": ["douyin_search_videos", "douyin_get_video_info"],
            "kuaishou": ["kuaishou_search_videos", "kuaishou_get_video_info"],
            "software": ["software_launch", "software_info", "software_list"],
            "wps": ["wps_open_document", "wps_create_document"],
            "wechat": ["wechat_send_message", "wechat_open_chat"],
            "qq": ["qq_send_message", "qq_open_chat"],
            "credential": ["credential_add", "credential_get", "credential_list", "credential_update", "credential_delete", "credential_search", "credential_auto_fill", "credential_export", "credential_import", "credential_categories"],
            "auto_fill": ["auto_fill_website", "auto_fill_application", "smart_auto_fill", "get_suggested_credentials", "validate_credential_format", "get_auto_fill_statistics"],
            "steam": ["steam_get_library", "steam_get_recent_activity", "steam_get_game_details", "steam_get_friend_comparison", "steam_open_store", "steam_analyze_habits", "steam_get_recommendations"],
            "desktop": ["desktop_scan", "desktop_launch"],
            "file": ["file_read", "file_write"],
            "system": ["run_command"],
            "video": ["play_video", "open_bilibili"],
            "automation": ["nl_automate", "nl_step_execute"],
            "utility": ["get_weather", "calculate", "translate", "send_email", "schedule_task"]
        }
        
        if category in category_keywords:
            keywords = category_keywords[category]
            return [tool for tool in self.tools_cache if tool["name"] in keywords]
        
        return []

class LAMAgentMCPAdapter:
    """LAM-Agent MCP适配器，将MCP工具集成到现有LamAgent中"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.server_started = False
    
    async def start(self):
        """启动MCP适配器"""
        if not self.server_started:
            await self.mcp_client.start_server()
            self.server_started = True
    
    async def stop(self):
        """停止MCP适配器"""
        if self.server_started:
            await self.mcp_client.stop_server()
            self.server_started = False
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行操作，优先使用MCP工具"""
        if not self.server_started:
            await self.start()
        
        # 映射现有操作到MCP工具
        action_mapping = {
            "open_website": "open_website",
            "open_bilibili": "open_bilibili",
            "play_video": "play_video",
            "automate_page": "web_automate",
            "bilibili_search_play": "bilibili_search_play",
            "nl_automate": "nl_automate",
            "search_web": "web_search",
            "create_file": "file_write",
            "read_file": "file_read",
            "run_command": "run_command",
            "get_weather": "get_weather",
            "calculate": "calculate",
            "translate": "translate",
            "send_email": "send_email",
            "schedule_task": "schedule_task",
            "site_search": "site_search",
            "browse_product": "browse_product",
            "play_video_generic": "play_video_generic",
            "add_to_cart": "add_to_cart",
            "nl_step_execute": "nl_step_execute",
            "fetch_page": "fetch_page",
            "bilibili_open_up": "bilibili_open_up",
            # Steam集成工具
            "steam_get_library": "steam_get_library",
            "steam_get_recent_activity": "steam_get_recent_activity",
            "steam_get_game_details": "steam_get_game_details",
            "steam_get_friend_comparison": "steam_get_friend_comparison",
            "steam_open_store": "steam_open_store",
            "steam_analyze_habits": "steam_analyze_habits",
            "steam_get_recommendations": "steam_get_recommendations",
            "steam_download_game": "steam_download_game",
            "steam_uninstall_game": "steam_uninstall_game",
            # Bilibili集成工具
            "bilibili_get_user_profile": "bilibili_get_user_profile",
            "bilibili_search_videos": "bilibili_search_videos",
            "bilibili_get_video_details": "bilibili_get_video_details",
            "bilibili_get_user_videos": "bilibili_get_user_videos",
            "bilibili_get_following_list": "bilibili_get_following_list",
            "bilibili_get_favorites": "bilibili_get_favorites",
            "bilibili_get_watch_later": "bilibili_get_watch_later",
            "bilibili_get_user_statistics": "bilibili_get_user_statistics",
            "bilibili_open_video": "bilibili_open_video",
            "bilibili_open_user": "bilibili_open_user",
            # 网站集成工具
            "website_open": "website_open",
            "website_search": "website_search",
            "website_summary": "website_summary",
            # 京东专用工具
            "jd_search_products": "jd_search_products",
            "jd_get_product_info": "jd_get_product_info",
            # 淘宝专用工具
            "taobao_search_products": "taobao_search_products",
            "taobao_get_product_info": "taobao_get_product_info",
            # 高德地图专用工具
            "amap_search_location": "amap_search_location",
            "amap_get_route": "amap_get_route",
            # 拼多多专用工具
            "pdd_search_products": "pdd_search_products",
            "pdd_get_product_info": "pdd_get_product_info",
            # 抖音专用工具
            "douyin_search_videos": "douyin_search_videos",
            "douyin_get_video_info": "douyin_get_video_info",
            # 快手专用工具
            "kuaishou_search_videos": "kuaishou_search_videos",
            "kuaishou_get_video_info": "kuaishou_get_video_info",
            # 桌面软件集成工具
            "software_launch": "software_launch",
            "software_info": "software_info",
            "software_list": "software_list",
            # WPS Office专用工具
            "wps_open_document": "wps_open_document",
            "wps_create_document": "wps_create_document",
            # 微信专用工具
            "wechat_send_message": "wechat_send_message",
            "wechat_open_chat": "wechat_open_chat",
            # QQ专用工具
            "qq_send_message": "qq_send_message",
            "qq_open_chat": "qq_open_chat",
            # 凭据数据库工具
            "credential_add": "credential_add",
            "credential_get": "credential_get",
            "credential_list": "credential_list",
            "credential_update": "credential_update",
            "credential_delete": "credential_delete",
            "credential_search": "credential_search",
            "credential_auto_fill": "credential_auto_fill",
            "credential_export": "credential_export",
            "credential_import": "credential_import",
            "credential_categories": "credential_categories",
            # 自动填充工具
            "auto_fill_website": "auto_fill_website",
            "auto_fill_application": "auto_fill_application",
            "smart_auto_fill": "smart_auto_fill",
            "get_suggested_credentials": "get_suggested_credentials",
            "validate_credential_format": "validate_credential_format",
            "get_auto_fill_statistics": "get_auto_fill_statistics"
        }
        
        mcp_tool_name = action_mapping.get(action)
        
        if mcp_tool_name:
            try:
                result = await self.mcp_client.call_tool(mcp_tool_name, params)
                return {
                    "success": True,
                    "action": action,
                    "result": result,
                    "source": "mcp"
                }
            except Exception as e:
                logger.error(f"MCP工具调用失败: {e}")
                # 回退到原有实现
                return await self._fallback_execute(action, params)
        else:
            # 使用原有实现
            return await self._fallback_execute(action, params)
    
    async def _fallback_execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """回退到原有执行器"""
        from src.tools.executor import executor
        
        # 这里需要将异步调用转换为同步调用
        # 或者修改executor以支持异步
        try:
            result = executor.execute_action(action, params)
            return {
                "success": True,
                "action": action,
                "result": result,
                "source": "legacy"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "legacy"
            }
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        if not self.server_started:
            await self.start()
        
        return await self.mcp_client.list_tools()

# 全局MCP适配器实例
mcp_adapter = LAMAgentMCPAdapter()

async def main():
    """测试MCP客户端"""
    adapter = LAMAgentMCPAdapter()
    
    try:
        await adapter.start()
        
        # 获取工具列表
        tools = await adapter.get_available_tools()
        print(f"可用工具: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 测试工具调用
        result = await adapter.execute_action("web_search", {"query": "Python MCP", "max_results": 3})
        print(f"搜索结果: {result}")
        
    finally:
        await adapter.stop()

if __name__ == "__main__":
    asyncio.run(main())
