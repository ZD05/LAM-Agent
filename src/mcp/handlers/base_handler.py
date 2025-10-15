#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP处理器基类，提供通用的错误处理和日志记录功能
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from ..core.base import BaseToolHandler

logger = logging.getLogger(__name__)

class BaseIntegrationHandler(BaseToolHandler):
    """基础集成处理器"""
    
    def __init__(self, integration_name: str):
        self.integration_name = integration_name
        self.action_handlers: Dict[str, Callable] = {}
    
    def register_action(self, action: str, handler: Callable):
        """注册动作处理器"""
        self.action_handlers[action] = handler
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理集成功能"""
        action = args.get("action")
        
        if not action:
            return {"error": "缺少action参数"}
        
        if action not in self.action_handlers:
            return {"error": f"不支持的操作: {action}"}
        
        try:
            handler = self.action_handlers[action]
            result = await self._execute_handler(handler, args)
            return result
        except Exception as e:
            logger.error(f"{self.integration_name}集成操作失败: {e}")
            return {"error": f"{self.integration_name}集成操作失败: {str(e)}"}
    
    async def _execute_handler(self, handler: Callable, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行处理器"""
        if asyncio.iscoroutinefunction(handler):
            return await handler(args)
        else:
            return handler(args)

class SimpleActionHandler(BaseToolHandler):
    """简单动作处理器"""
    
    def __init__(self, handler_name: str, action_func: Callable):
        self.handler_name = handler_name
        self.action_func = action_func
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理简单动作"""
        try:
            if asyncio.iscoroutinefunction(self.action_func):
                result = await self.action_func(args)
            else:
                result = self.action_func(args)
            return result
        except Exception as e:
            logger.error(f"{self.handler_name}操作失败: {e}")
            return {"error": f"{self.handler_name}操作失败: {str(e)}"}

def create_simple_handler(handler_name: str, action_func: Callable) -> SimpleActionHandler:
    """创建简单处理器"""
    return SimpleActionHandler(handler_name, action_func)

def create_integration_handler(integration_name: str) -> BaseIntegrationHandler:
    """创建集成处理器"""
    return BaseIntegrationHandler(integration_name)
