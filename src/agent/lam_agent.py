import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..config import settings
from ..tools.browser import automate_page
from ..tools.search import open_search_in_browser, web_search
from ..tools.desktop_integration import DesktopIntegration
from ..utils.validators import sanitize_text, validate_query, validate_url
from ..mcp import LAMAgentMCPAdapter

def _setup_logging():
    """配置日志系统"""
    if not logging.getLogger().handlers:
        from logging.handlers import RotatingFileHandler
        import os
        
        logging.getLogger().setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        log_dir = os.path.abspath(log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=2*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(console_handler)

# 初始化日志
_setup_logging()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "你是一个LAM（Language + Action Model）代理，具有直接执行操作的能力。\n"
    "你可以执行以下操作：\n"
    "1) 搜索网络获取最新信息\n"
    "2) 抓取和分析网页内容\n"
    "3) 打开网站\n"
    "4) 网页自动化操作（使用Playwright）\n"
    "5) 创建和读取文件\n"
    "6) 运行系统命令\n"
    "7) 计算数学表达式\n"
    "8) 翻译文本\n"
    "9) 发送邮件\n"
    "10) 安排任务\n"
    "11) 桌面文件管理（扫描、搜索、启动桌面文件和快捷方式）\n\n"
    "重要：当用户提出需求时，你应该：\n"
    "1. 分析用户意图和上下文\n"
    "2. 制定详细的执行计划\n"
    "3. 直接执行相应的操作\n"
    "4. 提供详细的结果和操作总结\n\n"
    "对于网页操作，你可以使用以下Playwright操作：\n"
    "- navigate: 导航到指定URL\n"
    "- click: 点击元素\n"
    "- type: 输入文本\n"
    "- press: 按下键盘按键\n"
    "- wait: 等待元素出现\n"
    "- sleep: 等待指定时间\n"
    "- scroll: 滚动页面\n"
    "- screenshot: 截图\n\n"
    "对于复杂多步骤指令，你应该：\n"
    "1. 分解为有序的步骤\n"
    "2. 识别每个步骤的目标平台和操作\n"
    "3. 生成相应的Playwright操作序列\n"
    "4. 按顺序执行所有步骤\n"
)

class LamAgent:
    def __init__(self, model: Optional[str] = None):
        self._model_name = model or settings.lam_agent_model
        self._llm: Optional[ChatOpenAI] = None
        self._is_running = False
        self._run_lock = threading.Lock()
        self._last_sig = ""
        self._last_sig_ts = 0.0
        
        # 初始化桌面集成功能
        self._desktop_integration = DesktopIntegration()
        
        # 初始化MCP适配器
        self._mcp_adapter = LAMAgentMCPAdapter()
        self._use_mcp = getattr(settings, 'use_mcp', True)  # 默认启用MCP
        
        # 验证API密钥
        if settings.use_deepseek:
            if not settings.deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY is required but not set")
        else:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required but not set")

    def _ensure_llm(self) -> ChatOpenAI:
        if self._llm is None:
            if settings.use_deepseek:
                self._llm = ChatOpenAI(
                    model=self._model_name,
                    api_key=settings.deepseek_api_key,
                    base_url=settings.deepseek_base_url,
                    temperature=0.2,
                )
            else:
                self._llm = ChatOpenAI(
                    model=self._model_name,
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                    temperature=0.2,
                )
        return self._llm
    
    def _generate_deepseek_plan(self, user_query: str, llm: ChatOpenAI) -> Dict[str, Any]:
        """使用DeepSeek生成执行计划"""
        try:
            prompt = f"""
用户查询: {user_query}

请仔细分析用户意图并生成详细的执行计划。特别注意：

1. 如果用户提到"打开B站"、"在B站搜索"、"B站播放"、"B站"等，应该选择automate操作，目标平台为bilibili.com
2. 如果用户提到"在淘宝"、"淘宝搜索"、"淘宝"等，应该选择automate操作，目标平台为taobao.com
3. 如果用户提到"在京东"、"京东搜索"、"京东"等，应该选择automate操作，目标平台为jd.com
4. 如果用户提到"在百度"、"百度搜索"、"百度"等，应该选择automate操作，目标平台为baidu.com
5. 如果只是简单的"搜索XXX"（没有指定平台），选择search操作，目标平台为browser
6. 对于复杂多步骤指令（包含"、"、"然后"、"接着"等），必须分解为多个步骤

操作类型说明：
- search: 通用网络搜索
- automate: 网页自动化操作（在特定网站内操作）
- browse: 浏览特定网页
- answer: 直接回答

请以JSON格式返回计划，例如：

        B站视频操作示例：
        {{
            "operation_type": "automate",
            "target_platform": "bilibili.com",
            "steps": [
                {{"action": "navigate", "url": "https://search.bilibili.com/all?keyword=Python教程"}},
                {{"action": "wait", "selector": "a[href*='/video/'], .video-item", "state": "visible"}},
                {{"action": "click", "selector": "a[href*='/video/']:first-of-type"}},
                {{"action": "wait", "selector": "video, .bpx-player-container", "state": "visible"}},
                {{"action": "video_play"}},
                {{"action": "sleep", "ms": 2000}},
                {{"action": "video_force_play"}},
                {{"action": "sleep", "ms": 2000}},
                {{"action": "video_click_play"}},
                {{"action": "sleep", "ms": 2000}},
                {{"action": "video_keyboard_play"}},
                {{"action": "sleep", "ms": 3000}}
            ],
            "context": "在B站搜索并播放Python教程视频"
        }}

        淘宝搜索示例：
        {{
            "operation_type": "automate",
            "target_platform": "taobao.com",
            "steps": [
                {{"action": "navigate", "url": "https://s.taobao.com/search?q=iPhone 15"}},
                {{"action": "wait", "selector": "a[href*='/item'], .item", "state": "visible"}}
            ],
            "context": "在淘宝搜索iPhone 15"
        }}

        京东搜索示例：
        {{
            "operation_type": "automate",
            "target_platform": "jd.com",
            "steps": [
                {{"action": "navigate", "url": "https://search.m.jd.com/Search?keyword=笔记本电脑"}},
                {{"action": "wait", "selector": "a[href*='/item'], .gl-item", "state": "visible"}}
            ],
            "context": "在京东搜索笔记本电脑"
        }}

        百度搜索示例：
        {{
            "operation_type": "automate",
            "target_platform": "baidu.com",
            "steps": [
                {{"action": "navigate", "url": "https://www.baidu.com/s?wd=今天天气"}},
                {{"action": "wait", "selector": "#content_left, .result", "state": "visible"}}
            ],
            "context": "在百度搜索今天天气"
        }}

        通用搜索示例：
        {{
            "operation_type": "search",
            "target_platform": "browser",
            "steps": [],
            "context": "搜索人工智能最新发展"
        }}
"""
            
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]).content.strip()
            
            # 尝试解析JSON
            try:
                plan = json.loads(response)
                return plan
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回默认计划
                return {
                    "operation_type": "search",
                    "target_platform": "browser",
                    "steps": [],
                    "context": user_query
                }
                
        except Exception as e:
            logger.error(f"生成DeepSeek计划失败: {e}")
            return {
                "operation_type": "search",
                "target_platform": "browser", 
                "steps": [],
                "context": user_query
            }
    
    def _execute_deepseek_plan(self, plan: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """执行DeepSeek生成的计划"""
        try:
            evidence = []
            operation_type = plan.get("operation_type", "search")
            target_platform = plan.get("target_platform", "browser")
            steps = plan.get("steps", [])
            
            logger.info(f"执行计划: {operation_type} - {target_platform} - {len(steps)}步骤")
            
            # 如果启用MCP，优先使用MCP工具
            if self._use_mcp:
                try:
                    import asyncio
                    mcp_result = asyncio.run(self._execute_with_mcp(plan, user_query))
                    if mcp_result.get("success"):
                        logger.info("MCP执行成功")
                        return mcp_result
                    else:
                        logger.warning(f"MCP执行失败，回退到传统方法: {mcp_result.get('error')}")
                except Exception as e:
                    logger.warning(f"MCP执行异常，回退到传统方法: {e}")
            
            if operation_type == "search":
                # 执行搜索操作
                if target_platform == "browser":
                    # 通用搜索
                    browser_result = open_search_in_browser(user_query)
                    if browser_result["success"]:
                        evidence.append({
                            "title": "浏览器搜索",
                            "href": "",
                            "body": f"已在浏览器中打开搜索结果: {browser_result['message']}"
                        })
                    
                    # 程序化搜索
                    sr = web_search(user_query, max_results=5)
                    evidence.extend(sr)
                else:
                    # 平台内搜索
                    search_result = self._search_on_platform(target_platform, user_query)
                    evidence.append({
                        "title": f"{target_platform}搜索",
                        "href": "",
                        "body": search_result.get("message", "搜索完成")
                    })
            
            elif operation_type == "browse":
                # 执行浏览操作
                url = plan.get("url", "")
                if url:
                    page_result = self._browse_page(url)
                    evidence.append({
                        "title": "页面浏览",
                        "href": url,
                        "body": page_result.get("content", "页面内容")
                    })
            
            elif operation_type == "automate":
                # 执行自动化操作
                if steps:
                    logger.info(f"执行自动化步骤: {len(steps)}个步骤")
                    automation_result = self._execute_automation_steps(steps, target_platform)
                    evidence.append({
                        "title": f"{target_platform}自动化操作",
                        "href": "",
                        "body": automation_result.get("message", "操作完成")
                    })
                else:
                    # 使用传统方法
                    logger.info(f"使用传统自动化方法: {target_platform}")
                    automation_result = self._execute_traditional_automation(user_query, target_platform)
                    evidence.append({
                        "title": f"{target_platform}传统自动化",
                        "href": "",
                        "body": automation_result.get("message", "操作完成")
                    })
            
            elif operation_type == "answer":
                # 直接回答
                evidence.append({
                    "title": "直接回答",
                    "href": "",
                    "body": "根据用户查询直接生成回答"
                })
            
            return {
                "success": True,
                "evidence": evidence,
                "operation_type": operation_type,
                "target_platform": target_platform,
                "steps_executed": len(steps)
            }
            
        except Exception as e:
            logger.error(f"执行DeepSeek计划失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "evidence": [{"title": "执行失败", "href": "", "body": f"执行计划时发生错误: {str(e)}"}]
            }
    
    def _search_on_platform(self, platform: str, query: str) -> Dict[str, Any]:
        """在指定平台搜索"""
        try:
            if platform == "bilibili.com":
                url = f"https://search.bilibili.com/all?keyword={query}"
            elif platform == "taobao.com":
                url = f"https://s.taobao.com/search?q={query}"
            elif platform == "jd.com":
                url = f"https://search.m.jd.com/Search?keyword={query}"
            elif platform == "baidu.com":
                url = f"https://www.baidu.com/s?wd={query}"
            else:
                return {"success": False, "message": f"不支持的平台: {platform}"}
            
            # 打开搜索页面
            import webbrowser
            webbrowser.open(url)
            
            return {"success": True, "message": f"已在{platform}搜索: {query}"}
            
        except Exception as e:
            return {"success": False, "message": f"搜索失败: {str(e)}"}
    
    def _browse_page(self, url: str) -> Dict[str, Any]:
        """浏览页面"""
        try:
            import webbrowser
            webbrowser.open(url)
            return {"success": True, "content": f"已打开页面: {url}"}
        except Exception as e:
            return {"success": False, "content": f"打开页面失败: {str(e)}"}
    
    def _execute_automation_steps(self, steps: List[Dict[str, Any]], target_platform: str) -> Dict[str, Any]:
        """执行自动化步骤"""
        try:
            # 检查步骤中是否有navigate操作，如果有则使用第一个navigate的URL
            target_url = f"https://{target_platform}" if not target_platform.startswith("http") else target_platform
            
            # 如果步骤中有navigate操作，使用第一个navigate的URL
            for step in steps:
                if step.get('action') == 'navigate' and step.get('url'):
                    target_url = step['url']
                    break
            
            # 执行Playwright操作
            result = automate_page(target_url, steps, headless=False)
            
            return {
                "success": result.get("success", False),
                "message": f"自动化操作完成: {len(steps)}个步骤",
                "details": result
            }
            
        except Exception as e:
            return {"success": False, "message": f"自动化操作失败: {str(e)}"}
    
    def _execute_traditional_automation(self, user_query: str, target_platform: str) -> Dict[str, Any]:
        """执行传统自动化操作"""
        try:
            # 根据平台和查询生成基本操作
            if "bilibili" in target_platform or "b站" in user_query.lower():
                steps = [
                    {"action": "navigate", "url": "https://www.bilibili.com"},
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": "input[placeholder*='搜索']"},
                    {"action": "type", "selector": "input[placeholder*='搜索']", "text": user_query},
                    {"action": "press", "selector": "input[placeholder*='搜索']", "key": "Enter"},
                    {"action": "wait", "selector": "a[href*='/video/']", "state": "visible"},
                    {"action": "click", "selector": "a[href*='/video/']:first-of-type"}
                ]
            elif "taobao" in target_platform or "淘宝" in user_query.lower():
                steps = [
                    {"action": "navigate", "url": "https://www.taobao.com"},
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": "input#q"},
                    {"action": "type", "selector": "input#q", "text": user_query},
                    {"action": "press", "selector": "input#q", "key": "Enter"},
                    {"action": "wait", "selector": "a[href*='/item']", "state": "visible"}
                ]
            else:
                # 默认搜索
                return self._search_on_platform("browser", user_query)
            
            return self._execute_automation_steps(steps, target_platform)
            
        except Exception as e:
            return {"success": False, "message": f"传统自动化失败: {str(e)}"}
    
    def _generate_final_answer(self, user_query: str, execution_result: Dict[str, Any], llm: ChatOpenAI) -> str:
        """生成最终答案"""
        try:
            evidence = execution_result.get("evidence", [])
            operation_type = execution_result.get("operation_type", "unknown")
            target_platform = execution_result.get("target_platform", "unknown")
            
            prompt = f"""
用户查询: {user_query}

执行结果:
- 操作类型: {operation_type}
- 目标平台: {target_platform}
- 执行状态: {'成功' if execution_result.get('success', False) else '失败'}

详细结果:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

请生成简洁明了的回答，总结执行结果。
"""
            
            response = llm.invoke([
                SystemMessage(content="你是一个智能助手，请根据执行结果生成简洁明了的回答。"),
                HumanMessage(content=prompt)
            ]).content.strip()
            
            return response
            
        except Exception as e:
            logger.error(f"生成最终答案失败: {e}")
            return f"操作完成，但生成回答时出现错误: {str(e)}"
    
    async def _execute_with_mcp(self, plan: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """使用MCP执行计划"""
        try:
            evidence = []
            operation_type = plan.get("operation_type", "search")
            target_platform = plan.get("target_platform", "browser")
            steps = plan.get("steps", [])
            
            # 启动MCP适配器
            await self._mcp_adapter.start()
            
            if operation_type == "search":
                # 使用MCP网络搜索工具
                result = await self._mcp_adapter.execute_action("search_web", {
                    "query": user_query,
                    "max_results": 5
                })
                
                if result.get("success"):
                    evidence.append({
                        "title": "MCP网络搜索",
                        "href": "",
                        "body": f"搜索完成，找到 {len(result.get('result', {}).get('results', []))} 个结果"
                    })
            
            elif operation_type == "automate":
                # 使用MCP网页自动化工具
                if steps:
                    # 找到目标URL
                    target_url = f"https://{target_platform}" if not target_platform.startswith("http") else target_platform
                    for step in steps:
                        if step.get('action') == 'navigate' and step.get('url'):
                            target_url = step['url']
                            break
                    
                    result = await self._mcp_adapter.execute_action("automate_page", {
                        "url": target_url,
                        "steps": steps
                    })
                    
                    if result.get("success"):
                        evidence.append({
                            "title": "MCP网页自动化",
                            "href": target_url,
                            "body": f"自动化操作完成: {len(steps)}个步骤"
                        })
            
            elif operation_type == "browse":
                # 使用MCP网页抓取工具
                url = plan.get("url", "")
                if url:
                    result = await self._mcp_adapter.execute_action("fetch_page", {
                        "url": url,
                        "timeout_ms": 15000
                    })
                    
                    if result.get("success"):
                        evidence.append({
                            "title": "MCP页面浏览",
                            "href": url,
                            "body": f"页面内容已获取: {result.get('result', {}).get('title', '未知标题')}"
                        })
            
            # 特殊平台处理
            if "bilibili" in target_platform or "b站" in user_query.lower():
                # 提取UP主名称（简单实现）
                up_name = user_query.replace("b站", "").replace("bilibili", "").strip()
                if not up_name:
                    up_name = "影视飓风"  # 默认UP主
                
                result = await self._mcp_adapter.execute_action("bilibili_search_play", {
                    "up_name": up_name,
                    "keep_open_seconds": 60
                })
                
                if result.get("success"):
                    evidence.append({
                        "title": "MCP B站操作",
                        "href": "",
                        "body": f"已搜索并播放UP主 {up_name} 的视频"
                    })
            
            return {
                "success": True,
                "evidence": evidence,
                "operation_type": operation_type,
                "target_platform": target_platform,
                "steps_executed": len(steps),
                "source": "mcp"
            }
            
        except Exception as e:
            logger.error(f"MCP执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "evidence": [{"title": "MCP执行失败", "href": "", "body": f"MCP执行时发生错误: {str(e)}"}]
            }
    
    def run(self, user_query: str) -> Dict[str, Union[str, int, List[Dict[str, str]], Dict[str, Any]]]:
        """运行LAM代理处理用户查询 - 使用DeepSeek统一处理"""
        # 验证输入
        user_query = validate_query(user_query)
        # 防重复与防重入：同一指令短时间内只执行一次
        sig = user_query.strip().lower()
        now = time.time()
        if self._last_sig == sig and (now - self._last_sig_ts) < 4.0:
            return {
                "plan": "skipped",
                "evidence_count": 0,
                "answer": "已忽略重复执行（短时间内收到相同指令）。",
                "sources": [],
                "evidence": []
            }
        
        if not self._run_lock.acquire(blocking=False):
            return {
                "plan": "busy",
                "evidence_count": 0,
                "answer": "当前正在处理上一条指令，请稍后再试。",
                "sources": [],
                "evidence": []
            }
        self._is_running = True
            
        try:
            logger.info(f"处理用户查询: {user_query[:100]}...")
            
            # 检查是否为桌面相关命令
            if self._is_desktop_command(user_query):
                logger.info("检测到桌面命令，使用桌面集成处理")
                execution_result = self._handle_desktop_command(user_query)
                answer = self._format_desktop_result(execution_result)
                
                self._last_sig = sig
                self._last_sig_ts = now
                
                return {
                    "plan": "desktop_command",
                    "execution_result": execution_result,
                    "answer": answer,
                    "evidence_count": 1,
                    "sources": [],
                    "evidence": [execution_result] if execution_result.get("success") else []
                }
            
            llm = self._ensure_llm()
            
            # 使用DeepSeek分析用户意图并生成执行计划
            execution_plan = self._generate_deepseek_plan(user_query, llm)
            logger.info(f"DeepSeek执行计划: {execution_plan}")
            
            # 执行DeepSeek生成的计划
            execution_result = self._execute_deepseek_plan(execution_plan, user_query)
            logger.info("DeepSeek计划执行完成")
            
            # 生成最终答案
            answer = self._generate_final_answer(user_query, execution_result, llm)
            logger.info("查询处理完成")
            
            self._last_sig = sig
            self._last_sig_ts = now
            
            return {
                "plan": execution_plan,
                "execution_result": execution_result,
                "answer": answer,
                "evidence_count": len(execution_result.get("evidence", [])),
                "evidence": execution_result.get("evidence", [])
            }
            
        except Exception as e:
            logger.error(f"代理运行失败: {e}")
            return {
                "plan": "error",
                "execution_result": {"success": False, "error": str(e)},
                "answer": f"抱歉，处理您的请求时出现错误：{str(e)}",
                "evidence_count": 0,
                "evidence": []
            }
        finally:
            self._is_running = False
            self._run_lock.release()
    
    def _is_desktop_command(self, user_query: str) -> bool:
        """检查是否为桌面相关命令"""
        desktop_keywords = [
            '扫描桌面', 'search desktop', 'scan desktop',
            '搜索桌面', 'search desktop files',
            '启动桌面', 'launch desktop', '启动文件',
            '桌面文件', 'desktop files', '快捷方式',
            'shortcut', '桌面应用', 'desktop app'
        ]
        
        user_query_lower = user_query.lower()
        return any(keyword in user_query_lower for keyword in desktop_keywords)
    
    def _handle_desktop_command(self, user_query: str) -> Dict[str, Any]:
        """处理桌面相关命令"""
        try:
            return self._desktop_integration.handle_desktop_command(user_query)
        except Exception as e:
            logger.error(f"处理桌面命令时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'处理桌面命令时出错: {str(e)}'
            }
    
    def _format_desktop_result(self, result: Dict[str, Any]) -> str:
        """格式化桌面操作结果"""
        if not result.get('success'):
            return f"[ERROR] 操作失败: {result.get('error', '未知错误')}"
        
        message = result.get('message', '操作完成')
        
        # 如果是扫描结果，添加详细信息
        if 'files' in result and result['files']:
            files = result['files']
            message += f"\n\n找到 {len(files)} 个文件/快捷方式:"
            
            for i, file_info in enumerate(files[:10], 1):  # 只显示前10个
                file_type = "[SHORTCUT]" if file_info.get('type') == 'shortcut' else "[FILE]"
                executable = "[EXE]" if file_info.get('executable') else ""
                message += f"\n{i:2d}. {file_type} {file_info['name']} {executable}"
                if file_info.get('description'):
                    message += f" - {file_info['description']}"
            
            if len(files) > 10:
                message += f"\n... 还有 {len(files) - 10} 个文件"
        
        # 如果是启动结果，添加启动信息
        if 'launch_result' in result:
            launch_result = result['launch_result']
            if launch_result.get('success'):
                message += f"\n\n[SUCCESS] 启动成功!"
                if launch_result.get('process_id'):
                    message += f" (进程ID: {launch_result['process_id']})"
            else:
                message += f"\n\n[ERROR] 启动失败: {launch_result.get('error', '未知错误')}"
        
        return message
