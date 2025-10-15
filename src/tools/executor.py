"""操作执行器 - 直接执行用户指令"""
import json
import logging
import os
import subprocess
import webbrowser
from datetime import datetime
from typing import Any, Dict, List, Optional

from .browser import (
    automate_page,
    generic_add_to_cart,
    generic_browse_product,
    generic_play_video,
    generic_site_search,
)
from .browser_context import browser_context
from .bilibili_integration import BilibiliIntegration
from .step_executor import execute_natural_language_instruction
from src.database.credential_db import credential_db

logger = logging.getLogger(__name__)


class ActionExecutor:
    """操作执行器，直接执行用户指令"""
    
    def __init__(self):
        self.supported_actions = {
            "open_website": self.open_website,
            "open_bilibili": self.open_bilibili,
            "play_video": self.play_video,
            "automate_page": self.action_automate_page,
            "bilibili_open_up": self.action_bilibili_open_up,
            "bilibili_play_video": self.action_bilibili_play_video,
            "nl_automate": self.action_nl_automate,
            "search_web": self.search_web,
            "create_file": self.create_file,
            "read_file": self.read_file,
            "run_command": self.run_command,
            "get_weather": self.get_weather,
            "calculate": self.calculate,
            "translate": self.translate,
            "send_email": self.send_email,
            "schedule_task": self.schedule_task,
            "site_search": self.site_search,
            "browse_product": self.browse_product,
            "play_video_generic": self.play_video_generic,
            "add_to_cart": self.add_to_cart_action,
            "nl_step_execute": self.nl_step_execute,
            # 淘宝拆分动作
            "taobao_search_product": self.action_taobao_search_product,
            "taobao_buy": self.action_taobao_buy,
        }
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定操作"""
        try:
            if action in self.supported_actions:
                logger.info(f"执行操作: {action}")
                result = self.supported_actions[action](params)
                return {
                    "success": True,
                    "action": action,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {action}",
                    "supported_actions": list(self.supported_actions.keys())
                }
        except Exception as e:
            logger.error(f"执行操作失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    def open_website(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """打开网站并检查自动登录"""
        url = params.get("url", "")
        if not url:
            return {"error": "缺少URL参数"}
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            # 首先使用浏览器自动化打开网站并检查登录
            from src.tools.auto_login import auto_login_manager
            from playwright.sync_api import sync_playwright
            from src.tools.browser_config_safe import get_safe_browser_args, get_safe_browser_context_config
            
            with sync_playwright() as p:
                from src.tools.browser_config_safe import get_launch_kwargs
                browser = p.chromium.launch(**get_launch_kwargs(headless=False))
                context = browser.new_context(**get_safe_browser_context_config())
                page = context.new_page()
                
                try:
                    # 打开页面
                    page.goto(url, timeout=30000)
                    
                    # 检查是否需要自动登录
                    login_result = auto_login_manager.auto_login_website(page, url)
                    
                    if login_result.get('success'):
                        if login_result.get('action') == 'no_login_required':
                            message = f"已打开网站: {url} (无需登录)"
                        elif login_result.get('action') == 'login_attempted':
                            message = f"已打开网站: {url} (自动登录成功)"
                        elif login_result.get('action') == 'no_credentials':
                            message = f"已打开网站: {url} (需要登录，但未找到凭据)"
                        else:
                            message = f"已打开网站: {url}"
                    else:
                        message = f"已打开网站: {url} (登录检查失败: {login_result.get('error', '')})"
                    
                    # 保持浏览器打开
                    return {
                        "message": message,
                        "url": url,
                        "action": "open_website",
                        "login_result": login_result
                    }
                    
                except Exception as e:
                    # 如果自动化失败，回退到简单打开
                    webbrowser.open(url)
                    return {
                        "message": f"已打开网站: {url} (自动化失败，使用默认浏览器)",
                        "url": url,
                        "action": "open_website",
                        "error": str(e)
                    }
                    
        except Exception as e:
            # 如果所有方法都失败，使用默认浏览器
            try:
                webbrowser.open(url)
                return {
                    "message": f"已打开网站: {url} (使用默认浏览器)",
                    "url": url,
                    "action": "open_website",
                    "error": str(e)
                }
            except Exception as e2:
                return {"error": f"打开网站失败: {str(e2)}"}
    
    def open_bilibili(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """打开B站并搜索视频"""
        try:
            # 打开B站主页
            webbrowser.open("https://www.bilibili.com")
            
            # 等待一下让页面加载
            import time
            time.sleep(2)
            
            # 尝试打开B站热门视频页面
            webbrowser.open("https://www.bilibili.com/v/popular/all")
            
            return {
                "message": "已打开B站并跳转到热门视频页面",
                "url": "https://www.bilibili.com",
                "action": "open_bilibili",
                "note": "请在浏览器中查看B站页面，可以手动搜索或浏览热门视频"
            }
        except Exception as e:
            return {"error": f"打开B站失败: {str(e)}"}
    
    def play_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """播放视频"""
        video_url = params.get("video_url", "")
        platform = params.get("platform", "bilibili")
        query = params.get("query", "")
        
        try:
            if platform == "bilibili":
                if not video_url:
                    # 如果没有指定视频URL，打开B站热门视频页面
                    webbrowser.open("https://www.bilibili.com/v/popular/all")
                    # 同时在浏览器中打开与原始指令相关的搜索引擎页，帮助用户快速选择视频
                    try:
                        if query:
                            from .search import open_search_in_browser
                            open_search_in_browser(query)
                    except Exception:
                        pass
                    return {
                        "message": "已打开B站热门视频页面，请手动选择要播放的视频",
                        "url": "https://www.bilibili.com/v/popular/all",
                        "action": "play_video"
                    }
                else:
                    webbrowser.open(video_url)
                    return {
                        "message": f"已打开视频: {video_url}",
                        "url": video_url,
                        "action": "play_video"
                    }
            else:
                webbrowser.open(video_url)
                return {
                    "message": f"已打开视频: {video_url}",
                    "url": video_url,
                    "action": "play_video"
                }
        except Exception as e:
            return {"error": f"播放视频失败: {str(e)}"}

    def action_automate_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """通用页面自动化: 在指定url上按步骤执行动作"""
        url = params.get("url")
        steps = params.get("steps", [])
        if not url:
            return {"error": "缺少url"}
        result = automate_page(url=url, steps=steps)
        return {"message": "页面自动化已执行", **result}

    def site_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """通用站内搜索: 在给定 url 上输入关键词并提交，尝试点击第一个结果。
        参数: { url: str, keyword: str, click_first_result?: bool }
        """
        url = params.get("url", "").strip()
        keyword = params.get("keyword", "").strip()
        click_first = bool(params.get("click_first_result", True))
        if not url or not keyword:
            return {"error": "缺少必需参数: url, keyword"}
        result = generic_site_search(url=url, keyword=keyword, click_first_result=click_first, headless=False)
        return {"message": f"已在站点内搜索: {keyword}", **result}

    def browse_product(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = params.get("url", "").strip()
        keyword = params.get("keyword", "").strip()
        match_text = params.get("match_text", "").strip()
        if not url or not keyword:
            return {"error": "缺少必需参数: url, keyword"}
        result = generic_browse_product(url=url, keyword=keyword, match_text=match_text or None, headless=False)
        return {"message": f"已浏览商品详情: {keyword}", **result}

    def play_video_generic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = params.get("url", "").strip()
        keyword = params.get("keyword", "").strip()
        match_text = params.get("match_text", "").strip()
        if not url or not keyword:
            return {"error": "缺少必需参数: url, keyword"}
        result = generic_play_video(url=url, keyword=keyword, match_text=match_text or None, headless=False)
        return {"message": f"已尝试播放视频: {keyword}", **result}

    def add_to_cart_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = params.get("url", "").strip()
        keyword = params.get("keyword", "").strip()
        match_text = params.get("match_text", "").strip()
        if not url or not keyword:
            return {"error": "缺少必需参数: url, keyword"}
        result = generic_add_to_cart(url=url, keyword=keyword, match_text=match_text or None, headless=False)
        return {"message": f"已尝试加入购物车: {keyword}", **result}


    def action_bilibili_open_up(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """只打开B站UP主主页，不播放视频。支持 keep_open_seconds。"""
        up_name = params.get("keyword") or params.get("up_name") or "影视飓风"
        keep_open_seconds = params.get("keep_open_seconds")
        keep_open_ms = int(keep_open_seconds * 1000) if keep_open_seconds else 60000
        
        try:
            # 使用浏览器上下文管理器
            if not browser_context.is_active:
                browser_context.start_browser(headless=False)
            
            # 导航到B站搜索页面
            search_url = f"https://search.bilibili.com/all?keyword={up_name}"
            nav_result = browser_context.navigate_to(search_url)
            
            if not nav_result.get('success'):
                return {"success": False, "error": nav_result.get('error')}
            
            # 执行主页导航步骤
            steps = [
                {"action": "sleep", "ms": 2000},
                {"action": "wait", "selector": "a.bili-video-card__info--owner, .bili-video-card", "state": "visible", "timeout": 8000},
                {"action": "sleep", "ms": 500},
                {"action": "click_any", "selectors": [
                    f"a.bili-video-card__info--owner:has-text('{up_name}')",
                    "a.bili-video-card__info--owner[href*='space.bilibili.com']",
                    f"a[href*='space.bilibili.com']:has-text('{up_name}')",
                    "a.bili-video-card__info--owner",
                    "a[href*='space.bilibili.com']"
                ]},
                {"action": "sleep", "ms": 2000}
            ]
            
            result = browser_context.execute_steps(steps)
            
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"成功进入 {up_name} 的主页",
                    "result": result
                }
            else:
                return {"success": False, "error": result.get('error')}
                
        except Exception as e:
            logger.error(f"B站主页导航失败: {e}")
            return {"success": False, "error": f"B站主页导航失败: {str(e)}"}

    def action_bilibili_play_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """播放B站视频 - 复用已打开的浏览器实例"""
        try:
            # 检查浏览器是否已启动
            if not browser_context.is_active:
                return {"success": False, "error": "浏览器未启动，请先执行主页导航"}
            
            # 获取当前页面信息
            page_info = browser_context.get_page_info()
            if not page_info.get('success'):
                return {"success": False, "error": "无法获取当前页面信息"}
            
            current_url = page_info.get('url', '')
            
            # 检查是否在UP主主页
            if 'space.bilibili.com' not in current_url:
                logger.warning(f"当前URL不包含space.bilibili.com: {current_url}")
                # 尝试导航到UP主主页
                up_name = params.get("up_name", "影视飓风")
                search_url = f"https://search.bilibili.com/all?keyword={up_name}"
                nav_result = browser_context.navigate_to(search_url)
                
                if not nav_result.get('success'):
                    return {"success": False, "error": "无法导航到UP主主页"}
                
                # 执行主页导航步骤
                steps = [
                    {"action": "sleep", "ms": 2000},
                    {"action": "wait", "selector": "a.bili-video-card__info--owner, .bili-video-card", "state": "visible", "timeout": 8000},
                    {"action": "sleep", "ms": 500},
                    {"action": "click_any", "selectors": [
                        f"a.bili-video-card__info--owner:has-text('{up_name}')",
                        "a.bili-video-card__info--owner[href*='space.bilibili.com']",
                        f"a[href*='space.bilibili.com']:has-text('{up_name}')",
                        "a.bili-video-card__info--owner",
                        "a[href*='space.bilibili.com']"
                    ]},
                    {"action": "sleep", "ms": 2000}
                ]
                
                nav_result = browser_context.execute_steps(steps)
                if not nav_result.get('success'):
                    return {"success": False, "error": "主页导航失败"}
            
            # 执行播放视频步骤
            steps = [
                {"action": "sleep", "ms": 1000},
                {"action": "wait", "selector": ".bili-video-card, .video-card, a[href*='/video/']", "state": "visible", "timeout": 8000},
                {"action": "sleep", "ms": 500},
                {"action": "click", "selector": ".bili-video-card:first-child a, .video-card:first-child a, a[href*='/video/']:first-child"},
                {"action": "sleep", "ms": 2000}
            ]
            
            result = browser_context.execute_steps(steps)
            
            if result.get('success'):
                return {
                    "success": True,
                    "message": "成功播放视频",
                    "result": result
                }
            else:
                return {"success": False, "error": result.get('error')}
                
        except Exception as e:
            logger.error(f"B站视频播放失败: {e}")
            return {"success": False, "error": f"B站视频播放失败: {str(e)}"}

    def action_nl_automate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """将自然语言解析为automate_page所需steps并执行。
        参数:
          - query: 自然语言指令（必填）
          - url: 目标站点初始URL（可选；能从query推断时可省略）
          - auth: { username, password, username_selector, password_selector, submit_selector }（可选）
        """
        query: str = params.get("query", "").strip()
        if not query:
            return {"error": "缺少自然语言指令 query"}

        url = params.get("url", "")
        steps: list = []

        query_lower = query.lower()
        # 站点推断
        if not url:
            if "b站" in query or "bilibili" in query_lower:
                url = "https://www.bilibili.com"
            elif "youtube" in query_lower:
                url = "https://www.youtube.com"
            elif "taobao" in query_lower or "淘宝" in query:
                url = "https://www.taobao.com"
            elif "jd" in query_lower or "京东" in query:
                url = "https://www.jd.com"
            else:
                # 默认Bing，留给后续 steps 的 goto 重定向
                url = "https://www.bing.com"

        # 登录支持
        auth = params.get("auth") or {}
        if auth and all(k in auth for k in ["username", "password", "username_selector", "password_selector"]):
            steps += [
                {"action": "wait", "selector": auth.get("username_selector"), "state": "visible"},
                {"action": "type", "selector": auth.get("username_selector"), "text": auth.get("username"), "secret": True},
                {"action": "type", "selector": auth.get("password_selector"), "text": auth.get("password"), "secret": True},
            ]
            if auth.get("submit_selector"):
                steps.append({"action": "click", "selector": auth.get("submit_selector")})

        # 搜索意图处理
        import re
        kw_match = re.search(r"搜索(.*)", query)
        if kw_match:
            keyword = kw_match.group(1).strip().replace("\u3002", "").strip()
            # 站点特异的搜索框选择器（多个备选，尽最大可能）
            search_selectors = [
                "input[type=search]",
                "input#nav-searchform input",
                "input[name=search_query]",
                "input#search",
                "input[aria-label='Search']",
                "input.s-input",
            ]
            steps += [
                {"action": "sleep", "ms": 600},
                {"action": "click", "selector": ", ".join(search_selectors)},
                {"action": "type", "selector": ", ".join(search_selectors), "text": keyword, "clear": True},
                {"action": "press", "selector": ", ".join(search_selectors), "key": "Enter"},
                {"action": "wait", "selector": "a, button", "state": "visible"},
            ]

        # 后续操作意图
        if any(k in query for k in ["播放第一个", "播放第1个", "播放视频", "播放"]):
            steps += [
                {"action": "wait", "selector": "a[href*='/video/'], ytd-video-renderer a#thumbnail, a[href*='/item']", "state": "visible"},
                {"action": "click", "selector": "a[href*='/video/'], ytd-video-renderer a#thumbnail"},
                {"action": "wait", "selector": "video", "state": "visible"},
                {"action": "sleep", "ms": 1000},
            ]

        if any(k in query for k in ["加入购物车", "加购", "add to cart", "购物车"]):
            steps += [
                {"action": "wait", "selector": "button:has-text('加入购物车'), #J_AddToCart, button[aria-label*='Add to cart']", "state": "visible"},
                {"action": "click", "selector": "button:has-text('加入购物车'), #J_AddToCart, button[aria-label*='Add to cart']"},
                {"action": "sleep", "ms": 500},
            ]

        # 外部追加步骤
        extra_steps = params.get("steps") or []
        steps += extra_steps

        # 同时打开搜索引擎
        search_opened = False
        if any(k in query for k in ["搜索", "查找", "search", "find"]):
            try:
                from .search import open_search_in_browser
                search_result = open_search_in_browser(query)
                if search_result.get("success"):
                    search_opened = True
                    logger.info(f"已同时打开搜索引擎: {search_result.get('message')}")
            except Exception as e:
                logger.warning(f"打开搜索引擎失败: {e}")

        result = automate_page(url=url, steps=steps, headless=False)
        
        # 在返回结果中添加搜索引擎打开状态
        if search_opened:
            result["search_opened"] = True
            result["message"] = result.get("message", "") + " (已同时打开搜索引擎)"
        
        return {"message": "已执行自然语言自动化", "url": url, "steps": steps, **result}
    
    def nl_step_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行自然语言指令的步骤化操作"""
        instruction = params.get("query", "").strip()
        if not instruction:
            return {"error": "缺少自然语言指令"}
        
        try:
            logger.info(f"开始执行步骤化指令: {instruction}")
            result = execute_natural_language_instruction(instruction)
            
            if result.get("success", False):
                logger.info(f"步骤化指令执行成功: {result.get('completed_steps', 0)}/{result.get('total_steps', 0)} 步骤完成")
            else:
                logger.warning(f"步骤化指令执行失败: {result.get('error', '未知错误')}")
            
            return {
                "message": "已执行步骤化指令",
                "instruction": instruction,
                **result
            }
        except Exception as e:
            logger.error(f"执行步骤化指令失败: {e}")
            return {
                "success": False,
                "error": f"执行步骤化指令失败: {str(e)}"
            }

    def action_taobao_search_product(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """淘宝搜索：店铺 -> 商品，停留在商品页。"""
        shop_name = params.get("shop_name", "乔尔的桌搭小店").strip()
        product_keyword = params.get("product_keyword", "金字塔").strip()
        try:
            if not browser_context.ensure_browser(headless=False):
                return {"success": False, "error": "无法启动浏览器"}

            # 直达店铺搜索结果
            shop_search_url = f"https://s.taobao.com/search?q={shop_name}&tab=shop"
            nav_shop = browser_context.navigate_to(shop_search_url)
            if not nav_shop.get('success'):
                return {"success": False, "error": nav_shop.get('error')}

            steps_open_shop = [
                {"action": "sleep", "ms": 1200},
                {"action": "click", "selector": f"a:has-text('{shop_name}')"},
                {"action": "sleep", "ms": 1800},
            ]
            res_open_shop = browser_context.execute_steps(steps_open_shop)
            if not res_open_shop.get('success'):
                return {"success": False, "error": "未能打开店铺"}

            # 店内搜索
            steps_search_product = [
                {"action": "sleep", "ms": 900},
                {"action": "click", "selector": "input[type='search'], input[name='q'], input[placeholder*='搜索']", "optional": True},
                {"action": "type", "selector": "input[type='search'], input[name='q'], input[placeholder*='搜索']", "text": product_keyword},
                {"action": "press", "selector": "input[type='search'], input[name='q'], input[placeholder*='搜索']", "key": "Enter"},
                {"action": "sleep", "ms": 1600},
                {"action": "click", "selector": "a[href*='item.taobao.com']:first-child, .item a[href*='item'], .item-card a[href*='item']"},
                {"action": "sleep", "ms": 1600},
            ]
            res_prod = browser_context.execute_steps(steps_search_product)
            if not res_prod.get('success'):
                return {"success": False, "error": "未能打开商品页"}

            return {"success": True, "message": "已打开商品页", "current_url": browser_context.get_page_info().get('url')}
        except Exception as e:
            logger.error(f"淘宝搜索失败: {e}")
            return {"success": False, "error": f"淘宝搜索失败: {str(e)}"}

    def action_taobao_buy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """在当前商品页进行购买/加购（与前序搜索保持上下文）。"""
        try:
            if not browser_context.ensure_browser(headless=False):
                return {"success": False, "error": "无法启动浏览器"}

            page_info = browser_context.get_page_info()
            url = page_info.get('url', '') if page_info.get('success') else ''
            if 'item.taobao.com' not in url:
                # 不在商品页则失败（避免误操作）
                return {"success": False, "error": "当前不在商品页，请先执行搜索并进入商品页"}

            steps_buy = [
                {"action": "sleep", "ms": 900},
                {"action": "click", "selector": ".J_Prop .J_TSaleProp li:not(.tb-out-of-stock):first-child, .sku .sku-list li:first-child", "optional": True},
                {"action": "sleep", "ms": 500},
                {"action": "click", "selector": "#J_LinkBuy, a:has-text('立即购买'), button:has-text('立即购买')", "optional": True},
                {"action": "sleep", "ms": 1400},
                {"action": "click", "selector": "#J_LinkBasket, a:has-text('加入购物车'), button:has-text('加入购物车')", "optional": True},
                {"action": "sleep", "ms": 1000},
            ]
            res_buy = browser_context.execute_steps(steps_buy)
            if not res_buy.get('success'):
                return {"success": False, "error": "购买操作失败"}

            return {"success": True, "message": "已尝试下单或加入购物车"}
        except Exception as e:
            logger.error(f"淘宝购买失败: {e}")
            return {"success": False, "error": f"淘宝购买失败: {str(e)}"}
    
    def search_web(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """搜索网络"""
        query = params.get("query", "")
        if not query:
            return {"error": "缺少搜索查询参数"}
        
        try:
            # 使用DuckDuckGo搜索
            from .search import web_search
            results = web_search(query, max_results=5)
            return {
                "message": f"搜索完成，找到 {len(results)} 个结果",
                "query": query,
                "results": results
            }
        except Exception as e:
            return {"error": f"搜索失败: {str(e)}"}
    
    def create_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建文件"""
        filename = params.get("filename", "")
        content = params.get("content", "")
        
        if not filename:
            return {"error": "缺少文件名参数"}
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "message": f"文件已创建: {filename}",
                "filename": filename,
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"创建文件失败: {str(e)}"}
    
    def read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """读取文件"""
        filename = params.get("filename", "")
        if not filename:
            return {"error": "缺少文件名参数"}
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "message": f"文件读取成功: {filename}",
                "filename": filename,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"读取文件失败: {str(e)}"}
    
    def run_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """运行系统命令"""
        command = params.get("command", "")
        if not command:
            return {"error": "缺少命令参数"}
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return {
                "message": f"命令执行完成: {command}",
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": "命令执行超时"}
        except Exception as e:
            return {"error": f"命令执行失败: {str(e)}"}
    
    def get_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取天气信息"""
        city = params.get("city", "北京")
        
        try:
            # 这里可以集成真实的天气API
            # 目前返回模拟数据
            return {
                "message": f"获取 {city} 天气信息",
                "city": city,
                "weather": "晴天",
                "temperature": "25°C",
                "humidity": "60%",
                "note": "这是模拟数据，实际使用时需要集成天气API"
            }
        except Exception as e:
            return {"error": f"获取天气失败: {str(e)}"}
    
    def calculate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算数学表达式"""
        expression = params.get("expression", "")
        if not expression:
            return {"error": "缺少计算表达式参数"}
        
        try:
            # 安全的数学计算
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return {"error": "表达式包含不安全的字符"}
            
            result = eval(expression)
            return {
                "message": f"计算完成: {expression}",
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {"error": f"计算失败: {str(e)}"}
    
    def translate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """翻译文本"""
        text = params.get("text", "")
        target_lang = params.get("target_lang", "en")
        
        if not text:
            return {"error": "缺少要翻译的文本"}
        
        try:
            # 这里可以集成真实的翻译API
            # 目前返回模拟结果
            return {
                "message": f"翻译完成: {text[:50]}...",
                "original": text,
                "translated": f"[{target_lang}] {text}",
                "target_language": target_lang,
                "note": "这是模拟翻译，实际使用时需要集成翻译API"
            }
        except Exception as e:
            return {"error": f"翻译失败: {str(e)}"}
    
    def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送邮件"""
        to = params.get("to", "")
        subject = params.get("subject", "")
        content = params.get("content", "")
        
        if not all([to, subject, content]):
            return {"error": "缺少邮件参数 (to, subject, content)"}
        
        try:
            # 这里可以集成真实的邮件发送服务
            return {
                "message": "邮件发送成功",
                "to": to,
                "subject": subject,
                "content": content,
                "note": "这是模拟发送，实际使用时需要配置邮件服务"
            }
        except Exception as e:
            return {"error": f"发送邮件失败: {str(e)}"}
    
    def schedule_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """安排任务"""
        task = params.get("task", "")
        time = params.get("time", "")
        
        if not task:
            return {"error": "缺少任务描述"}
        
        try:
            return {
                "message": "任务已安排",
                "task": task,
                "scheduled_time": time or "立即执行",
                "note": "这是模拟安排，实际使用时需要集成任务调度系统"
            }
        except Exception as e:
            return {"error": f"安排任务失败: {str(e)}"}


# 全局执行器实例
executor = ActionExecutor()
