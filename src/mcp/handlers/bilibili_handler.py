#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bilibili工具处理器
"""

import logging
from typing import Dict, Any
from ..core.base import BaseToolHandler

logger = logging.getLogger(__name__)

class BilibiliSearchPlayHandler(BaseToolHandler):
    """B站搜索播放处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理B站搜索播放"""
        up_name = args["up_name"]
        keep_open_seconds = args.get("keep_open_seconds", 60)
        
        try:
            from src.tools.bilibili import search_and_play_first_video_strict
            result = search_and_play_first_video_strict(up_name, keep_open_seconds)
            return result
        except Exception as e:
            logger.error(f"B站搜索播放失败: {e}")
            return {"error": f"B站搜索播放失败: {str(e)}"}

class BilibiliOpenUpHandler(BaseToolHandler):
    """B站打开UP主页面处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理B站打开UP主页面"""
        up_name = args["up_name"]
        
        try:
            from src.tools.bilibili import open_up_homepage
            result = open_up_homepage(up_name)
            return result
        except Exception as e:
            logger.error(f"B站打开UP主页面失败: {e}")
            return {"error": f"B站打开UP主页面失败: {str(e)}"}

class BilibiliIntegrationHandler(BaseToolHandler):
    """B站集成处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理B站集成功能"""
        action = args["action"]
        
        try:
            from src.tools.bilibili_integration import bilibili_integration
            
            if action == "get_user_profile":
                uid = args["uid"]
                result = bilibili_integration.get_user_profile(uid)
            elif action == "search_videos":
                keyword = args["keyword"]
                page = args.get("page", 1)
                result = bilibili_integration.search_videos(keyword, page)
            elif action == "get_video_details":
                bvid = args["bvid"]
                result = bilibili_integration.get_video_details(bvid)
            elif action == "get_user_videos":
                uid = args["uid"]
                page = args.get("page", 1)
                result = bilibili_integration.get_user_videos(uid, page)
            elif action == "get_following_list":
                uid = args["uid"]
                page = args.get("page", 1)
                result = bilibili_integration.get_following_list(uid, page)
            elif action == "get_user_favorites":
                uid = args["uid"]
                page = args.get("page", 1)
                result = bilibili_integration.get_user_favorites(uid, page)
            elif action == "get_watch_later_list":
                uid = args["uid"]
                page = args.get("page", 1)
                result = bilibili_integration.get_watch_later_list(uid, page)
            elif action == "get_user_statistics":
                uid = args["uid"]
                result = bilibili_integration.get_user_statistics(uid)
            elif action == "open_bilibili_video":
                bvid = args["bvid"]
                result = bilibili_integration.open_bilibili_video(bvid)
            elif action == "open_bilibili_user":
                uid = args["uid"]
                result = bilibili_integration.open_bilibili_user(uid)
            else:
                return {"error": f"不支持的操作: {action}"}
            
            return result
        except Exception as e:
            logger.error(f"B站集成操作失败: {e}")
            return {"error": f"B站集成操作失败: {str(e)}"}

