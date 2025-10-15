"""
步骤执行引擎
按照解析的操作步骤顺序执行任务
"""
import logging
import time
import webbrowser
from typing import List, Dict, Any, Optional
from .nl_parser import OperationStep
from .browser import automate_page
from .search import open_search_in_browser
from ..config import settings

logger = logging.getLogger(__name__)


class StepExecutor:
    """步骤执行引擎"""
    
    def __init__(self):
        self.execution_log = []
        self.current_step = 0
        self.total_steps = 0
    
    def execute_steps(self, steps: List[OperationStep]) -> Dict[str, Any]:
        """
        执行操作步骤列表
        
        Args:
            steps: 操作步骤列表
            
        Returns:
            执行结果
        """
        self.execution_log = []
        self.current_step = 0
        self.total_steps = len(steps)
        
        logger.info(f"开始执行{self.total_steps}个操作步骤")
        
        results = {
            "success": True,
            "total_steps": self.total_steps,
            "completed_steps": 0,
            "failed_steps": 0,
            "execution_log": [],
            "final_result": None
        }
        
        try:
            for i, step in enumerate(steps):
                self.current_step = i + 1
                logger.info(f"执行步骤 {self.current_step}/{self.total_steps}: {step.description}")
                
                step_result = self._execute_single_step(step)
                self.execution_log.append({
                    "step": self.current_step,
                    "operation": {
                        "description": step.description,
                        "action": step.action,
                        "target": step.target,
                        "query": step.query
                    },
                    "result": step_result,
                    "timestamp": time.time()
                })
                
                if step_result.get("success", False):
                    results["completed_steps"] += 1
                    logger.info(f"步骤 {self.current_step} 执行成功")
                else:
                    results["failed_steps"] += 1
                    logger.error(f"步骤 {self.current_step} 执行失败: {step_result.get('error', '未知错误')}")
                    
                    # 如果关键步骤失败，停止执行
                    if self._is_critical_step(step):
                        logger.error("关键步骤失败，停止执行")
                        results["success"] = False
                        break
                
                # 步骤间等待
                if i < len(steps) - 1:
                    time.sleep(2)
            
            results["execution_log"] = self.execution_log
            results["final_result"] = self._generate_final_result()
            
        except Exception as e:
            logger.error(f"执行过程中发生异常: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        logger.info(f"执行完成: 成功{results['completed_steps']}步，失败{results['failed_steps']}步")
        return results
    
    def _execute_single_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行单个步骤"""
        try:
            if step.action == "open":
                return self._execute_open_step(step)
            elif step.action == "search":
                return self._execute_search_step(step)
            elif step.action == "play":
                return self._execute_play_step(step)
            elif step.action == "click":
                return self._execute_click_step(step)
            elif step.action == "enter":
                return self._execute_enter_step(step)
            elif step.action == "browse":
                return self._execute_browse_step(step)
            elif step.action == "view":
                return self._execute_view_step(step)
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作类型: {step.action}"
                }
        except Exception as e:
            logger.error(f"执行步骤失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_open_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行打开操作"""
        if step.target == "browser":
            # 在浏览器中搜索
            search_query = step.query or step.target
            try:
                result = open_search_in_browser(search_query)
                return {
                    "success": result.get("success", False),
                    "message": f"已在浏览器中搜索: {search_query}",
                    "details": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"搜索失败: {e}"
                }
        else:
            # 直接打开网站：对 mouse_only_sites 使用 Playwright 打开并仅鼠标操作
            url = f"https://{step.target}" if not step.target.startswith("http") else step.target
            try:
                hostname = step.target
                if any(hostname.endswith(site) for site in settings.mouse_only_sites):
                    steps = [
                        {"action": "sleep", "ms": 1200},
                        # 简单可见性等待，避免修改DOM
                        {"action": "wait", "selector": "body", "state": "visible", "timeout": 10000}
                    ]
                    result = automate_page(url, steps, headless=False)
                    return {
                        "success": result.get("success", False),
                        "message": f"已以鼠标优先模式打开: {url}",
                        "details": result
                    }
                else:
                    webbrowser.open(url)
                    return {
                        "success": True,
                        "message": f"已打开网站: {url}",
                        "url": url
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"打开网站失败: {e}"
                }
    
    def _execute_search_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行搜索操作"""
        if not step.query:
            return {
                "success": False,
                "error": "搜索关键词为空"
            }
        
        # 根据目标网站选择搜索方式
        if step.target == "bilibili.com":
            return self._search_on_bilibili(step.query)
        elif step.target == "youtube.com":
            return self._search_on_youtube(step.query)
        elif step.target == "taobao.com":
            return self._search_on_taobao(step.query)
        else:
            # 通用搜索
            return self._search_generic(step.target, step.query)
    
    def _execute_play_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行播放操作"""
        if step.target == "bilibili.com":
            return self._play_on_bilibili(step.query)
        elif step.target == "youtube.com":
            return self._play_on_youtube(step.query)
        else:
            return self._play_generic(step.target, step.query)
    
    def _execute_click_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行点击操作"""
        return {
            "success": True,
            "message": f"点击操作: {step.query}",
            "note": "点击操作需要具体的页面元素定位"
        }
    
    def _execute_enter_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行进入操作"""
        return self._execute_open_step(step)
    
    def _execute_browse_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行浏览操作"""
        return self._execute_open_step(step)
    
    def _execute_view_step(self, step: OperationStep) -> Dict[str, Any]:
        """执行查看操作"""
        return self._execute_open_step(step)
    
    def _search_on_bilibili(self, query: str) -> Dict[str, Any]:
        """在B站搜索 - 使用浏览器上下文管理器"""
        try:
            from .browser_context import browser_context
            
            # 检查浏览器是否已启动
            if not browser_context.is_active:
                # 如果浏览器未启动，直接导航到搜索页面
                search_url = f"https://search.bilibili.com/all?keyword={query}"
                browser_context.start_browser(headless=False)
                nav_result = browser_context.navigate_to(search_url)
                
                if not nav_result.get('success'):
                    return {"success": False, "error": nav_result.get('error')}
                
                return {
                    "success": True,
                    "message": f"成功搜索: {query}",
                    "result": nav_result
                }
            else:
                # 浏览器已启动，在当前页面进行搜索
                # 检查当前页面是否是B站
                page_info = browser_context.get_page_info()
                current_url = page_info.get('url', '')
                
                if 'bilibili.com' not in current_url:
                    # 不在B站，导航到B站首页
                    nav_result = browser_context.navigate_to("https://www.bilibili.com")
                    if not nav_result.get('success'):
                        return {"success": False, "error": nav_result.get('error')}
                
                # 执行搜索步骤
                steps = [
                    # 1. 等待页面加载
                    {"action": "sleep", "ms": 2000},
                    
                    # 2. 关闭可能的弹窗
                    {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn", "optional": True},
                    {"action": "sleep", "ms": 500},
                    
                    # 3. 点击搜索框
                    {"action": "click", "selector": ".nav-search-input input, input[placeholder*='搜索'], .search-input input"},
                    {"action": "sleep", "ms": 300},
                    
                    # 4. 清空并输入搜索关键词
                    {"action": "type", "selector": ".nav-search-input input, input[placeholder*='搜索'], .search-input input", 
                     "text": query, "clear": True},
                    {"action": "sleep", "ms": 500},
                    
                    # 5. 按回车搜索
                    {"action": "press", "selector": ".nav-search-input input, input[placeholder*='搜索'], .search-input input", "key": "Enter"},
                    {"action": "sleep", "ms": 2000},
                    
                    # 6. 等待搜索结果加载
                    {"action": "wait", "selector": "a[href*='/video/'], .video-item, .bili-video-card", "state": "visible"},
                    {"action": "sleep", "ms": 1000},
                ]
                
                result = browser_context.execute_steps(steps)
                
                return {
                    "success": result.get("success", False),
                    "message": f"已在B站搜索: {query}",
                    "details": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"B站搜索失败: {e}"
            }
    
    def _search_on_youtube(self, query: str) -> Dict[str, Any]:
        """在YouTube搜索"""
        try:
            steps = [
                {"action": "sleep", "ms": 1000},
                {"action": "click", "selector": "input#search"},
                {"action": "type", "selector": "input#search", "text": query, "clear": True},
                {"action": "press", "selector": "input#search", "key": "Enter"},
                {"action": "wait", "selector": "ytd-video-renderer", "state": "visible"},
            ]
            
            result = automate_page("https://www.youtube.com", steps, headless=False)
            return {
                "success": result.get("success", False),
                "message": f"已在YouTube搜索: {query}",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"YouTube搜索失败: {e}"
            }
    
    def _search_on_taobao(self, query: str) -> Dict[str, Any]:
        """在淘宝搜索"""
        try:
            steps = [
                {"action": "sleep", "ms": 3000},
                {"action": "click", "selector": "input#q, input[placeholder*='搜索'], input[placeholder*='search'], .search-input input"},
                {"action": "type", "selector": "input#q, input[placeholder*='搜索'], input[placeholder*='search'], .search-input input", "text": query, "clear": True},
                {"action": "press", "selector": "input#q, input[placeholder*='搜索'], input[placeholder*='search'], .search-input input", "key": "Enter"},
                {"action": "wait", "selector": "a[href*='/item'], .item, .product-item", "state": "visible"},
            ]
            
            result = automate_page("https://www.taobao.com", steps, headless=False)
            return {
                "success": result.get("success", False),
                "message": f"已在淘宝搜索: {query}",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"淘宝搜索失败: {e}"
            }
    
    def _search_on_jd(self, query: str) -> Dict[str, Any]:
        """在京东搜索"""
        try:
            steps = [
                {"action": "sleep", "ms": 3000},
                {"action": "click", "selector": "input#key, input[placeholder*='搜索'], input[placeholder*='search'], .search-input input"},
                {"action": "type", "selector": "input#key, input[placeholder*='搜索'], input[placeholder*='search'], .search-input input", "text": query, "clear": True},
                {"action": "press", "selector": "input#key, input[placeholder*='搜索'], input[placeholder*='search'], .search-input input", "key": "Enter"},
                {"action": "wait", "selector": "a[href*='/product'], .item, .product-item, .goods-item", "state": "visible"},
            ]
            
            result = automate_page("https://www.jd.com", steps, headless=False)
            return {
                "success": result.get("success", False),
                "message": f"已在京东搜索: {query}",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"京东搜索失败: {e}"
            }
    
    def _search_on_baidu(self, query: str) -> Dict[str, Any]:
        """在百度搜索"""
        try:
            steps = [
                {"action": "sleep", "ms": 3000},
                {"action": "click", "selector": "input#kw, input[placeholder*='搜索'], input[placeholder*='search'], .s_ipt"},
                {"action": "type", "selector": "input#kw, input[placeholder*='搜索'], input[placeholder*='search'], .s_ipt", "text": query, "clear": True},
                {"action": "press", "selector": "input#kw, input[placeholder*='搜索'], input[placeholder*='search'], .s_ipt", "key": "Enter"},
                {"action": "wait", "selector": "a[href], .result, .c-container", "state": "visible"},
            ]
            
            result = automate_page("https://www.baidu.com", steps, headless=False)
            return {
                "success": result.get("success", False),
                "message": f"已在百度搜索: {query}",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"百度搜索失败: {e}"
            }
    
    def _search_generic(self, target: str, query: str) -> Dict[str, Any]:
        """通用搜索"""
        try:
            # 如果目标是browser，使用搜索引擎搜索
            if target == "browser":
                result = open_search_in_browser(query)
                return {
                    "success": result.get("success", False),
                    "message": f"已在浏览器中搜索: {query}",
                    "details": result
                }
            
            # 对于特定网站，先打开网站，然后在网站内搜索
            url = f"https://{target}" if not target.startswith("http") else target
            
            # 根据网站类型选择搜索方式
            if target == "taobao.com":
                return self._search_on_taobao(query)
            elif target == "jd.com":
                return self._search_on_jd(query)
            elif target == "baidu.com":
                return self._search_on_baidu(query)
            else:
                # 通用网站搜索
                steps = [
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": "input[type=search], input#search, input[name=q], input[placeholder*='搜索'], input[placeholder*='search']"},
                    {"action": "type", "selector": "input[type=search], input#search, input[name=q], input[placeholder*='搜索'], input[placeholder*='search']", "text": query, "clear": True},
                    {"action": "press", "selector": "input[type=search], input#search, input[name=q], input[placeholder*='搜索'], input[placeholder*='search']", "key": "Enter"},
                    {"action": "wait", "selector": "a[href], button, .item, .product", "state": "visible"},
                ]
                
                result = automate_page(url, steps, headless=False)
                return {
                    "success": result.get("success", False),
                    "message": f"已在{target}搜索: {query}",
                    "details": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"通用搜索失败: {e}"
            }
    
    def _play_on_bilibili(self, query: str) -> Dict[str, Any]:
        """在B站播放视频 - 使用浏览器上下文管理器"""
        try:
            from .browser_context import browser_context
            
            # 检查浏览器是否已启动
            if not browser_context.is_active:
                # 如果浏览器未启动，直接导航到搜索页面
                search_url = f"https://search.bilibili.com/all?keyword={query}"
                browser_context.start_browser(headless=False)
                nav_result = browser_context.navigate_to(search_url)
                
                if not nav_result.get('success'):
                    return {"success": False, "error": nav_result.get('error')}
                
                # 执行播放步骤
                steps = [
                    {"action": "sleep", "ms": 2000},
                    {"action": "wait", "selector": "a[href*='/video/'], .video-item, .bili-video-card", "state": "visible"},
                    {"action": "sleep", "ms": 1000},
                    {"action": "click", "selector": "a[href*='/video/']:first-of-type, .video-item a:first-of-type, .bili-video-card a:first-of-type"},
                    {"action": "sleep", "ms": 3000},
                    {"action": "wait", "selector": ".bpx-player-container, .bilibili-player, video", "state": "visible"},
                    {"action": "sleep", "ms": 2000},
                ]
                
                result = browser_context.execute_steps(steps)
            else:
                # 浏览器已启动，在当前页面进行搜索和播放
                page_info = browser_context.get_page_info()
                current_url = page_info.get('url', '')
                
                if 'bilibili.com' not in current_url:
                    # 不在B站，导航到B站首页
                    nav_result = browser_context.navigate_to("https://www.bilibili.com")
                    if not nav_result.get('success'):
                        return {"success": False, "error": nav_result.get('error')}
                
                # 执行搜索和播放步骤
                steps = [
                    # 1. 等待页面加载
                    {"action": "sleep", "ms": 2000},
                    
                    # 2. 关闭可能的弹窗
                    {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn", "optional": True},
                    {"action": "sleep", "ms": 500},
                    
                    # 3. 点击搜索框
                    {"action": "click", "selector": ".nav-search-input input, input[placeholder*='搜索'], .search-input input"},
                    {"action": "sleep", "ms": 300},
                    
                    # 4. 输入搜索关键词
                    {"action": "type", "selector": ".nav-search-input input, input[placeholder*='搜索'], .search-input input", 
                     "text": query, "clear": True},
                    {"action": "sleep", "ms": 500},
                    
                    # 5. 按回车搜索
                    {"action": "press", "selector": ".nav-search-input input, input[placeholder*='搜索'], .search-input input", "key": "Enter"},
                    {"action": "sleep", "ms": 2000},
                    
                    # 6. 等待搜索结果加载
                    {"action": "wait", "selector": "a[href*='/video/'], .video-item, .bili-video-card", "state": "visible"},
                    {"action": "sleep", "ms": 1000},
                    
                    # 7. 使用光标点击第一个视频链接
                    {"action": "click", "selector": "a[href*='/video/']:first-of-type, .video-item a:first-of-type, .bili-video-card a:first-of-type"},
                    {"action": "sleep", "ms": 3000},
                    
                    # 8. 等待视频页面加载
                    {"action": "wait", "selector": ".bpx-player-container, .bilibili-player, video", "state": "visible"},
                    {"action": "sleep", "ms": 2000},
                ]
                
                result = browser_context.execute_steps(steps)
            return {
                "success": result.get("success", False),
                "message": f"已在B站搜索并播放视频: {query}",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"B站播放失败: {e}"
            }
    
    def _play_on_youtube(self, query: str) -> Dict[str, Any]:
        """在YouTube播放视频"""
        try:
            steps = [
                {"action": "sleep", "ms": 1000},
                {"action": "click", "selector": "ytd-video-renderer a#thumbnail"},
                {"action": "wait", "selector": "video", "state": "visible"},
                {"action": "sleep", "ms": 2000},
            ]
            
            result = automate_page("https://www.youtube.com", steps, headless=False)
            return {
                "success": result.get("success", False),
                "message": f"已在YouTube播放视频: {query}",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"YouTube播放失败: {e}"
            }
    
    def _play_generic(self, target: str, query: str) -> Dict[str, Any]:
        """通用播放"""
        if target == "bilibili.com":
            # 在B站中搜索并播放视频
            return self._play_on_bilibili(query)
        elif target == "youtube.com":
            # 在YouTube中搜索并播放视频
            return self._play_on_youtube(query)
        else:
            # 对于其他平台，先搜索然后播放第一个视频
            try:
                # 先搜索视频
                search_result = self._search_generic(target, query)
                if not search_result.get("success", False):
                    return search_result
                
                # 然后尝试播放第一个视频
                steps = [
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": "a[href*='/video/'], a[href*='watch'], .video-item a, .video-card a"},
                    {"action": "wait", "selector": "video, .player", "state": "visible"},
                    {"action": "sleep", "ms": 3000},
                    # 优先使用点击播放
                    {"action": "video_click_play"},
                    {"action": "sleep", "ms": 2000},
                    # 如果点击播放失败，尝试其他方式
                    {"action": "video_play"},
                    {"action": "sleep", "ms": 2000},
                ]
                
                url = f"https://{target}" if not target.startswith("http") else target
                result = automate_page(url, steps, headless=False)
                return {
                    "success": result.get("success", False),
                    "message": f"已在{target}播放视频: {query}",
                    "details": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"播放失败: {e}"
                }
    
    def _is_critical_step(self, step: OperationStep) -> bool:
        """判断是否为关键步骤"""
        # 打开操作通常是关键的
        return step.action == "open"
    
    def _generate_final_result(self) -> str:
        """生成最终结果描述"""
        if not self.execution_log:
            return "没有执行任何步骤"
        
        success_count = sum(1 for log in self.execution_log if log["result"].get("success", False))
        total_count = len(self.execution_log)
        
        return f"执行完成: {success_count}/{total_count} 个步骤成功"


def execute_natural_language_instruction(instruction: str) -> Dict[str, Any]:
    """
    执行自然语言指令的便捷函数
    
    Args:
        instruction: 自然语言指令
        
    Returns:
        执行结果
    """
    from .nl_parser import parse_natural_language_instruction
    
    # 解析指令
    steps = parse_natural_language_instruction(instruction)
    
    if not steps:
        return {
            "success": False,
            "error": "无法解析指令",
            "total_steps": 0,
            "completed_steps": 0,
            "failed_steps": 0,
            "execution_log": []
        }
    
    # 执行步骤
    executor = StepExecutor()
    return executor.execute_steps(steps)
