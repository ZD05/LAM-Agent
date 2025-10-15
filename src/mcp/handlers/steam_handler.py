#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Steam工具处理器
"""

import logging
from typing import Dict, Any
from ..core.base import BaseToolHandler

logger = logging.getLogger(__name__)

class SteamIntegrationHandler(BaseToolHandler):
    """Steam集成处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理Steam集成功能"""
        action = args["action"]
        
        try:
            from src.tools.steam_integration import steam_integration
            
            if action == "get_game_library":
                result = steam_integration.get_game_library()
            elif action == "get_recent_activity":
                result = steam_integration.get_recent_activity()
            elif action == "get_game_details":
                appid = args["appid"]
                result = steam_integration.get_game_details(appid)
            elif action == "get_friend_comparison":
                result = steam_integration.get_friend_comparison()
            elif action == "open_steam_store":
                result = steam_integration.open_steam_store()
            elif action == "analyze_gaming_habits":
                result = steam_integration.analyze_gaming_habits()
            elif action == "get_game_recommendations":
                result = steam_integration.get_game_recommendations()
            elif action == "download_game":
                appid = args["appid"]
                result = steam_integration.download_game(appid)
            elif action == "uninstall_game":
                appid = args["appid"]
                result = steam_integration.uninstall_game(appid)
            else:
                return {"error": f"不支持的操作: {action}"}
            
            return result
        except Exception as e:
            logger.error(f"Steam集成操作失败: {e}")
            return {"error": f"Steam集成操作失败: {str(e)}"}


