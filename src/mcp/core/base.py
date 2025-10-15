#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP核心基础类和接口
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable

class BaseToolHandler(ABC):
    """工具处理器基类"""
    
    @abstractmethod
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        pass
    
    def get_tool_name(self) -> str:
        """获取工具名称"""
        return self.__class__.__name__.replace('Handler', '').lower()

class BaseToolRegistry(ABC):
    """工具注册器基类"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
    
    @abstractmethod
    def register_tools(self) -> None:
        """注册工具"""
        pass
    
    def register_tool(self, tool: MCPTool) -> None:
        """注册单个工具"""
        self.tools[tool.name] = tool
        logger.debug(f"注册工具: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[MCPTool]:
        """列出所有工具"""
        return list(self.tools.values())
    
    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self.tools.keys())

class MCPResponse:
    """MCP响应封装类"""
    
    def __init__(self, success: bool = True, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        if self.success:
            return {"success": True, "data": self.data}
        else:
            return {"success": False, "error": self.error}
    
    @classmethod
    def success_response(cls, data: Any = None) -> 'MCPResponse':
        """创建成功响应"""
        return cls(success=True, data=data)
    
    @classmethod
    def error_response(cls, error: str) -> 'MCPResponse':
        """创建错误响应"""
        return cls(success=False, error=error)

class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, registry: BaseToolRegistry):
        self.registry = registry
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> MCPResponse:
        """执行工具"""
        try:
            tool = self.registry.get_tool(tool_name)
            if not tool:
                return MCPResponse.error_response(f"工具 '{tool_name}' 不存在")
            
            # 验证参数
            if not self._validate_args(args, tool.input_schema):
                return MCPResponse.error_response("参数验证失败")
            
            # 执行工具
            result = await tool.handler(args)
            return MCPResponse.success_response(result)
            
        except Exception as e:
            logger.error(f"执行工具 '{tool_name}' 失败: {e}")
            return MCPResponse.error_response(f"执行工具失败: {str(e)}")
    
    def _validate_args(self, args: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证参数"""
        # 简化的参数验证
        if "required" in schema:
            required_fields = schema["required"]
            for field in required_fields:
                if field not in args:
                    logger.warning(f"缺少必需参数: {field}")
                    return False
        return True
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        tools = []
        for tool in self.registry.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        return tools


