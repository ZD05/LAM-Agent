#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
浏览器上下文管理器
用于在多个操作之间共享浏览器实例和页面状态
"""

import logging
import os
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from .browser_config_safe import get_safe_browser_args, get_safe_browser_context_config

logger = logging.getLogger(__name__)

class BrowserContextManager:
    """浏览器上下文管理器"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.current_page: Optional[Page] = None
        self.current_url: str = ""
        self.is_active = False
        # 可选：默认会话存储路径（用于保持登录状态）
        self.default_storage_state_path: Optional[str] = None
        
    def _is_obj_closed(self, obj: Any) -> bool:
        try:
            return hasattr(obj, "is_closed") and obj.is_closed()
        except Exception:
            return True

    def _needs_restart(self) -> bool:
        if not self.is_active:
            return True
        if self.playwright is None:
            return True
        if self.browser is None or self._is_obj_closed(self.browser):
            return True
        if self.context is None or self._is_obj_closed(self.context):
            return True
        if self.current_page is None or self._is_obj_closed(self.current_page):
            return True
        return False

    def ensure_browser(self, headless: bool = False) -> bool:
        """确保浏览器、上下文与页面可用，不可用则重启。"""
        try:
            if not self._needs_restart():
                return True

            # 先尝试关闭残留
            try:
                if self.browser:
                    self.browser.close()
            except Exception:
                pass
            try:
                if self.playwright:
                    self.playwright.stop()
            except Exception:
                pass

            self.playwright = None
            self.browser = None
            self.context = None
            self.current_page = None
            self.is_active = False

            # 启动全新实例
            return self.start_browser(headless=headless)
        except Exception as e:
            logger.error(f"确保浏览器可用失败: {e}")
            return False

    def start_browser(self, headless: bool = False) -> bool:
        """启动浏览器（若已可用则直接复用）"""
        try:
            if not self._needs_restart():
                logger.info("浏览器已启动，复用现有实例")
                return True

            logger.info("启动新的浏览器实例")
            self.playwright = sync_playwright().start()

            from .browser_config_safe import get_launch_kwargs
            self.browser = self.playwright.chromium.launch(
                **get_launch_kwargs(headless=headless)
            )

            context_cfg = get_safe_browser_context_config()
            # 若设置了默认存储状态且文件存在，则加载以复用登录
            if self.default_storage_state_path and os.path.exists(self.default_storage_state_path):
                context_cfg['storage_state'] = self.default_storage_state_path

            self.context = self.browser.new_context(**context_cfg)
            self.current_page = self.context.new_page()
            self.is_active = True

            logger.info("浏览器启动成功")
            return True

        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            return False
    
    def navigate_to(self, url: str) -> Dict[str, Any]:
        """导航到指定URL"""
        try:
            if not self.ensure_browser(headless=False):
                return {"success": False, "error": "无法启动或恢复浏览器"}
            
            logger.info(f"导航到: {url}")
            try:
                self.current_page.goto(url, timeout=20000)
            except Exception as e:
                # 尝试一次自愈：出现EPIPE/已关闭则重启并重试
                msg = str(e)
                if any(k in msg for k in ["EPIPE", "has been closed", "Target page, context or browser has been closed"]):
                    logger.warning(f"导航异常，尝试自愈重试: {msg}")
                    if not self.ensure_browser(headless=False):
                        return {"success": False, "error": f"无法恢复浏览器: {msg}"}
                    self.current_page.goto(url, timeout=20000)
                else:
                    raise
            self.current_url = url
            
            return {
                "success": True,
                "url": url,
                "title": self.current_page.title(),
                "message": f"成功导航到: {url}"
            }
            
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return {"success": False, "error": f"导航失败: {str(e)}"}
    
    def execute_steps(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """在当前页面上执行步骤"""
        def _run_steps() -> Dict[str, Any]:
            logs: List[str] = []
            for i, step in enumerate(steps):
                action = step.get('action', '').lower()
                logger.info(f"执行步骤 {i+1}: {action}")

                if action == 'sleep':
                    ms = step.get('ms', 1000)
                    self.current_page.wait_for_timeout(ms)
                    logs.append(f"等待 {ms}ms")

                elif action == 'wait':
                    selector = step.get('selector')
                    state = step.get('state', 'visible')
                    timeout = step.get('timeout', 10000)
                    if selector:
                        self.current_page.wait_for_selector(selector, state=state, timeout=timeout)
                        logs.append(f"等待元素: {selector}")

                elif action == 'click':
                    selector = step.get('selector')
                    optional = step.get('optional', False)
                    if selector:
                        try:
                            self.current_page.click(selector)
                            logs.append(f"点击: {selector}")
                        except Exception as e:
                            if optional:
                                logs.append(f"跳过可选点击: {selector} (未找到元素)")
                            else:
                                raise e

                elif action == 'click_any':
                    selectors = step.get('selectors', [])
                    clicked = False
                    for selector in selectors:
                        try:
                            self.current_page.click(selector, timeout=2000)
                            logs.append(f"点击成功: {selector}")
                            clicked = True
                            break
                        except Exception:
                            continue
                    if not clicked:
                        logs.append(f"点击失败，尝试的选择器: {selectors}")

                elif action == 'type':
                    selector = step.get('selector')
                    text = step.get('text', '')
                    if selector and text:
                        self.current_page.fill(selector, text)
                        logs.append(f"输入文本: {text}")

                elif action == 'keyboard_type':
                    text = step.get('text', '')
                    delay = step.get('delay', 0)
                    if text:
                        self.current_page.keyboard.type(text, delay=delay)
                        logs.append(f"键盘输入: {text}")

                elif action == 'press':
                    selector = step.get('selector')
                    key = step.get('key')
                    if selector and key:
                        self.current_page.locator(selector).press(key)
                        logs.append(f"在 {selector} 上按键: {key}")

                elif action == 'press_global':
                    key = step.get('key')
                    if key:
                        self.current_page.keyboard.press(key)
                        logs.append(f"按键: {key}")

            return {
                "success": True,
                "current_url": self.current_page.url,
                "title": self.current_page.title(),
                "logs": logs,
                "message": f"成功执行 {len(steps)} 个步骤"
            }

        # 主执行流程，附带一次自愈重试
        try:
            if not self.ensure_browser(headless=False):
                return {"success": False, "error": "无法启动或恢复浏览器"}
            return _run_steps()
        except Exception as e:
            msg = str(e)
            if any(k in msg for k in ["EPIPE", "has been closed", "Target page, context or browser has been closed"]):
                logger.warning(f"步骤执行异常，尝试自愈重试: {msg}")
                if not self.ensure_browser(headless=False):
                    return {"success": False, "error": f"无法恢复浏览器: {msg}"}
                try:
                    return _run_steps()
                except Exception as e2:
                    logger.error(f"重试后仍失败: {e2}")
                    return {"success": False, "error": f"执行步骤失败: {e2}"}
            else:
                logger.error(f"执行步骤失败: {e}")
                return {"success": False, "error": f"执行步骤失败: {e}"}
    
    def get_page_info(self) -> Dict[str, Any]:
        """获取当前页面信息"""
        try:
            if not self.ensure_browser(headless=False):
                return {"success": False, "error": "无法启动或恢复浏览器"}
            
            return {
                "success": True,
                "url": self.current_page.url,
                "title": self.current_page.title(),
                "is_active": self.is_active
            }
            
        except Exception as e:
            logger.error(f"获取页面信息失败: {e}")
            return {"success": False, "error": f"获取页面信息失败: {str(e)}"}

    # --------- 会话存储管理（保持登录） ---------
    def set_default_storage_state(self, path: str) -> None:
        try:
            self.default_storage_state_path = path
            logger.info(f"已设置默认会话存储路径: {path}")
        except Exception as e:
            logger.error(f"设置会话存储路径失败: {e}")

    def save_storage_state(self, path: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not self.context:
                return {"success": False, "error": "无可用上下文可保存"}
            target = path or self.default_storage_state_path
            if not target:
                return {"success": False, "error": "未提供存储路径"}
            # 确保目录存在
            os.makedirs(os.path.dirname(target), exist_ok=True)
            self.context.storage_state(path=target)
            logger.info(f"会话状态已保存: {target}")
            return {"success": True, "path": target}
        except Exception as e:
            logger.error(f"保存会话状态失败: {e}")
            return {"success": False, "error": f"保存会话状态失败: {e}"}
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
                logger.info("浏览器已关闭")
            
            if self.playwright:
                self.playwright.stop()
                logger.info("Playwright已停止")
                
            self.is_active = False
            self.current_page = None
            self.context = None
            self.browser = None
            self.playwright = None
            
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")

# 全局浏览器上下文管理器实例
browser_context = BrowserContextManager()
