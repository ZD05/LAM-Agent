#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网站自动登录处理器
"""

import logging
from typing import Dict, Any
from ..core.base import BaseToolHandler

logger = logging.getLogger(__name__)

class AutoLoginHandler(BaseToolHandler):
    """网站自动登录处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理网站自动登录"""
        try:
            from src.tools.auto_login import auto_login_manager
            from playwright.async_api import async_playwright
            from src.tools.browser_config_safe import get_safe_browser_args, get_safe_browser_context_config
            
            url = args.get("url")
            if not url:
                return {"error": "缺少URL参数"}
            
            async with async_playwright() as p:
                from src.tools.browser_config_safe import get_launch_kwargs
                browser = await p.chromium.launch(**get_launch_kwargs(headless=False))
                context = await browser.new_context(**get_safe_browser_context_config())
                page = await context.new_page()
                
                try:
                    # 打开页面
                    await page.goto(url, timeout=30000)
                    
                    # 执行自动登录
                    result = auto_login_manager.auto_login_website(page, url)
                    
                    # 如果登录成功，保持浏览器打开一段时间
                    if result.get('success') and result.get('action') == 'login_attempted':
                        # 等待用户确认登录结果
                        import asyncio
                        await asyncio.sleep(5)
                    
                    return result
                    
                finally:
                    # 不立即关闭浏览器，让用户查看结果
                    pass
                    
        except Exception as e:
            logger.error(f"自动登录处理失败: {e}")
            return {"error": f"自动登录失败: {str(e)}"}

class WebsiteLoginHandler(BaseToolHandler):
    """网站登录状态检查处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """检查网站登录状态"""
        try:
            from src.tools.auto_login import auto_login_manager
            from playwright.async_api import async_playwright
            from src.tools.browser_config_safe import get_safe_browser_args, get_safe_browser_context_config
            
            url = args.get("url")
            if not url:
                return {"error": "缺少URL参数"}
            
            async with async_playwright() as p:
                from src.tools.browser_config_safe import get_launch_kwargs
                browser = await p.chromium.launch(**get_launch_kwargs(headless=True))
                context = await browser.new_context(**get_safe_browser_context_config())
                page = await context.new_page()
                
                try:
                    # 打开页面
                    await page.goto(url, timeout=30000)
                    
                    # 检查是否需要登录
                    needs_login = auto_login_manager.detect_login_required(page)
                    
                    # 检查是否有凭据
                    has_credentials = auto_login_manager.get_credentials_for_site(url) is not None
                    
                    return {
                        "success": True,
                        "needs_login": needs_login,
                        "has_credentials": has_credentials,
                        "url": url,
                        "message": "登录状态检查完成"
                    }
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"登录状态检查失败: {e}")
            return {"error": f"登录状态检查失败: {str(e)}"}
