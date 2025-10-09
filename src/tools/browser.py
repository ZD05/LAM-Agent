import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from ..config import settings
from .browser_config import (
    get_browser_args, 
    get_browser_context_config,
    get_video_play_selectors,
    get_video_container_selectors,
    get_search_selectors,
    get_result_link_selectors,
    get_add_to_cart_selectors,
    get_proxy_config,
)

logger = logging.getLogger(__name__)


def fetch_page(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 15000) -> Dict[str, Any]:
    """使用Playwright抓取网页内容"""
    if not url or not url.strip():
        raise ValueError("URL不能为空")
    
    # 验证URL格式
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"无效的URL格式: {url}")
    
    if timeout_ms <= 0 or timeout_ms > 60000:
        raise ValueError("超时时间必须在1-60000毫秒之间")
    
    try:
        logger.info(f"开始抓取页面: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=settings.lam_browser_headless,
                channel="msedge",  # 使用Edge浏览器
                args=get_browser_args()
            )
            context = browser.new_context(**get_browser_context_config())
            page = context.new_page()
            
            try:
                page.goto(url, timeout=timeout_ms)
                if wait_selector:
                    page.wait_for_selector(wait_selector, timeout=timeout_ms)
                html = page.content()
                title = page.title()
            except PlaywrightTimeoutError as e:
                logger.warning(f"页面加载超时: {e}")
                html = page.content()
                title = page.title() or "页面标题获取失败"
            finally:
                browser.close()

        soup = BeautifulSoup(html, "lxml")
        text_content = soup.get_text("\n", strip=True)
        
        logger.info(f"页面抓取完成: {title}")
        return {"title": title, "html": html, "text": text_content}
        
    except Exception as e:
        logger.error(f"页面抓取失败: {e}")
        raise RuntimeError(f"页面抓取失败: {str(e)}") from e


def automate_page(
    url: str,
    steps: List[Dict[str, Any]],
    headless: Optional[bool] = None,
    timeout_ms: int = 20000,
    keep_open_ms: Optional[int] = None,
) -> Dict[str, Any]:
    """使用Playwright在真实浏览器中执行一系列页面操作。

    steps: 每一步为一个dict，支持的action:
      - goto: { action: 'goto', url }
      - type: { action: 'type', selector, text, clear: bool }
      - click: { action: 'click', selector }
      - press: { action: 'press', selector, key }
      - wait: { action: 'wait', selector, state: 'visible'|'attached'|'detached'|'hidden' }
      - sleep: { action: 'sleep', ms }
      - evaluate: { action: 'evaluate', script }  # 执行简单脚本
    返回: { success, title, current_url, logs: [...], screenshot(optional) }
    """
    if not url or not url.strip():
        raise ValueError("URL不能为空")

    logs: List[str] = []
    headless = headless if headless is not None else settings.lam_browser_headless

    try:
        with sync_playwright() as p:
            proxy = get_proxy_config()
            launch_kwargs = {
                "headless": headless,
                "channel": "msedge",  # 使用Edge浏览器
                "args": get_browser_args(),
            }
            if proxy:
                launch_kwargs["proxy"] = proxy
            browser = p.chromium.launch(**launch_kwargs)

            context_kwargs = get_browser_context_config()
            if proxy:
                context_kwargs["proxy"] = proxy
            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            def log(msg: str):
                logger.info(msg)
                logs.append(msg)

            # 进入初始URL
            log(f"打开页面: {url}")
            page.goto(url, timeout=timeout_ms)
            
            # 按用户要求：不再注入任何脚本，避免修改页面标签

            for step in steps or []:
                action = (step.get('action') or '').lower()
                if action == 'goto':
                    u = step.get('url')
                    if not u:
                        continue
                    log(f"跳转: {u}")
                    page.goto(u, timeout=timeout_ms)
                elif action == 'type':
                    selector = step.get('selector')
                    text = step.get('text', '')
                    if not selector:
                        continue
                    if step.get('clear'):
                        page.fill(selector, '')
                    is_secret = bool(step.get('secret')) or ('password' in selector.lower())
                    if is_secret:
                        log(f"输入: selector={selector}, text=**** (已隐藏)")
                        page.fill(selector, text)
                    else:
                        log(f"输入: selector={selector}, text={text}")
                        page.type(selector, text, delay=20)
                elif action == 'click':
                    selector = step.get('selector')
                    if not selector:
                        continue
                    log(f"点击: selector={selector}")
                    try:
                        # 使用较短超时处理可选点击，避免长时间阻塞
                        click_timeout = 2000 if step.get('optional') else timeout_ms
                        if step.get('new_page'):
                            try:
                                with context.expect_page() as new_page_info:
                                    page.click(selector, timeout=click_timeout)
                                new_p = new_page_info.value
                                # 等待新页面加载到可交互
                                try:
                                    new_p.wait_for_load_state('domcontentloaded', timeout=timeout_ms)
                                except Exception:
                                    pass
                                page = new_p  # 切换后续操作到新页面
                                log("已切换到新打开的页面")
                            except Exception as e:
                                # 若未捕获到popup，尝试常规点击（某些站点同页打开）
                                log(f"未捕获到新页面，将尝试当前页点击: {e}")
                                page.click(selector, timeout=click_timeout)
                        else:
                            page.click(selector, timeout=click_timeout)
                    except Exception as e:
                        if step.get('optional'):
                            log(f"可选点击跳过: {e}")
                        else:
                            raise
                elif action == 'press':
                    selector = step.get('selector')
                    key = step.get('key', 'Enter')
                    if not selector:
                        continue
                    log(f"按键: selector={selector}, key={key}")
                    page.press(selector, key)
                elif action == 'press_global':
                    # 不依赖选择器的全局按键（例如使用'/'唤起搜索框）
                    key = step.get('key', 'Enter')
                    log(f"全局按键: key={key}")
                    page.keyboard.press(key)
                elif action == 'wait_any':
                    selectors = step.get('selectors') or []
                    if not selectors:
                        continue
                    log(f"等待任一可见: {selectors}")
                    import time as _time
                    deadline = _time.time() + (int(step.get('timeout', max(timeout_ms, 10000)))/1000)
                    found = False
                    last_err = None
                    while _time.time() < deadline and not found:
                        for sel in selectors:
                            try:
                                page.wait_for_selector(sel, state='visible', timeout=2000)
                                found = True
                                break
                            except Exception as e:
                                last_err = e
                                continue
                        if not found:
                            page.wait_for_timeout(200)
                    if not found and not step.get('optional'):
                        raise last_err or RuntimeError('未找到任何可见元素')
                elif action == 'click_any':
                    selectors = step.get('selectors') or []
                    if not selectors:
                        continue
                    log(f"尝试点击任一: {selectors}")
                    clicked = False
                    for sel in selectors:
                        try:
                            if step.get('new_page'):
                                try:
                                    with context.expect_page() as new_page_info:
                                        page.click(sel, timeout=2500)
                                    new_p = new_page_info.value
                                    try:
                                        new_p.wait_for_load_state('domcontentloaded', timeout=timeout_ms)
                                    except Exception:
                                        pass
                                    page = new_p
                                    log(f"已切换到新页面 (由 {sel} 打开)")
                                    clicked = True
                                    break
                                except Exception:
                                    # fallback 普通点击
                                    page.click(sel, timeout=2500)
                                    clicked = True
                                    break
                            else:
                                page.click(sel, timeout=2500)
                                clicked = True
                                break
                        except Exception:
                            continue
                    if not clicked and not step.get('optional'):
                        raise RuntimeError('未能点击任一目标')
                elif action == 'wait':
                    selector = step.get('selector')
                    state = step.get('state', 'visible')
                    if not selector:
                        continue
                    log(f"等待: selector={selector}, state={state}")
                    try:
                        page.wait_for_selector(selector, state=state, timeout=timeout_ms)
                    except Exception as e:
                        if step.get('optional'):
                            log(f"可选等待跳过: {e}")
                        else:
                            raise
                elif action == 'wait_url':
                    expected = step.get('includes') or step.get('contains') or ''
                    timeout_local = int(step.get('timeout', timeout_ms))
                    log(f"等待URL包含: {expected}")
                    import time as _time
                    start = _time.time()
                    ok = False
                    while _time.time() - start < (timeout_local/1000):
                        if expected and expected in page.url:
                            ok = True
                            break
                        page.wait_for_timeout(200)
                    if not ok:
                        raise RuntimeError(f"URL未到达预期: {page.url}")
                elif action == 'wait_video_ready':
                    # 等待可见且具有有效尺寸的视频或播放器容器
                    log("等待视频元素可见且尺寸有效")
                    import time as _time
                    deadline = _time.time() + (int(step.get('timeout', 15000))/1000)
                    ready = False
                    candidates = [
                        'video',
                        '.bpx-player-container',
                        '.bilibili-player',
                        "[class*='player']",
                        "[class*='video']",
                    ]
                    while _time.time() < deadline and not ready:
                        for sel in candidates:
                            try:
                                loc = page.locator(sel).first
                                page.wait_for_timeout(150)
                                if loc.is_visible(timeout=800):
                                    try:
                                        loc.scroll_into_view_if_needed(timeout=1000)
                                    except Exception:
                                        pass
                                    box = loc.bounding_box()
                                    if box and box.get('width', 0) > 100 and box.get('height', 0) > 80:
                                        log(f"视频元素就绪: {sel} {box}")
                                        ready = True
                                        break
                            except Exception:
                                continue
                        if not ready:
                            page.wait_for_timeout(250)
                    if not ready:
                        raise RuntimeError("视频元素未就绪或尺寸过小")
                elif action == 'sleep':
                    ms = int(step.get('ms', 500))
                    import time
                    log(f"暂停: {ms}ms")
                    time.sleep(ms/1000)
                elif action == 'evaluate':
                    script = step.get('script', '')
                    if not script:
                        continue
                    log("执行脚本 evaluate")
                    try:
                        result = page.evaluate(script)
                        if result is not None:
                            log(f"脚本返回结果: {str(result)[:1000]}...")  # 限制长度避免日志过长
                        else:
                            log("脚本执行完成，无返回值")
                    except Exception as e:
                        log(f"脚本执行失败: {e}")
                elif action == 'keyboard_type':
                    # 全局键盘输入，不绑定具体选择器
                    text = step.get('text', '')
                    delay = int(step.get('delay', 20))
                    hidden = bool(step.get('secret'))
                    log(f"键盘输入: text={'****' if hidden else text}")
                    page.keyboard.type(text, delay=delay)
                elif action == 'video_play':
                    # 仅使用真实鼠标操作尝试播放（不注入、不修改DOM、不操作iframe）
                    log("使用鼠标方式尝试播放视频")
                    try:
                        def click_with_mouse_on_locator(loc):
                            try:
                                loc.scroll_into_view_if_needed(timeout=2000)
                                box = loc.bounding_box()
                                if not box:
                                    return False
                                x = box['x'] + box['width'] / 2
                                y = box['y'] + box['height'] / 2
                                page.mouse.move(x, y)
                                page.wait_for_timeout(120)
                                page.mouse.click(x, y)
                                page.wait_for_timeout(250)
                                page.mouse.dblclick(x, y, delay=80)
                                return True
                            except Exception:
                                return False

                        # 优先点击显式播放控件
                        candidates = get_video_play_selectors()

                        clicked = False
                        for sel in candidates:
                            try:
                                loc = page.locator(sel).first
                                if loc.is_visible(timeout=1500):
                                    if click_with_mouse_on_locator(loc):
                                        log(f"鼠标点击播放控件成功: {sel}")
                                        clicked = True
                                        break
                            except Exception:
                                continue

                        # 若仍未点击成功，点击播放器容器中心
                        if not clicked:
                            containers = get_video_container_selectors()
                            for sel in containers:
                                try:
                                    loc = page.locator(sel).first
                                    if loc.is_visible(timeout=1500):
                                        if click_with_mouse_on_locator(loc):
                                            log(f"鼠标点击播放器容器成功: {sel}")
                                            clicked = True
                                            break
                                except Exception:
                                    continue

                        if not clicked:
                            log("未能通过鼠标方式触发播放")
                    except Exception as e:
                        log(f"鼠标播放失败: {e}")
                elif action == 'video_force_play':
                    # 强制播放视频
                    log("强制播放视频")
                    try:
                        page.evaluate("""
                            // 强制所有视频播放
                            const videos = document.querySelectorAll('video');
                            for (const video of videos) {
                                video.muted = false;
                                video.volume = 1.0;
                                video.play().catch(() => {
                                    // 如果失败，尝试先静音播放
                                    video.muted = true;
                                    video.play().then(() => {
                                        video.muted = false;
                                    });
                                });
                            }
                        """)
                        log("强制播放完成")
                    except Exception as e:
                        log(f"强制播放失败: {e}")
                elif action == 'video_click_play':
                    # 使用真实鼠标移动+点击，专门针对B站优化
                    log("使用光标点击方式尝试播放B站视频")
                    try:
                        def click_with_mouse_on_locator(loc):
                            """真实鼠标点击操作，模拟人类行为"""
                            try:
                                # 1. 滚动到元素可见
                                loc.scroll_into_view_if_needed(timeout=2000)
                                
                                # 2. 获取元素位置
                                box = loc.bounding_box()
                                if not box:
                                    return False
                                
                                # 3. 计算点击坐标（元素中心）
                                x = box['x'] + box['width'] / 2
                                y = box['y'] + box['height'] / 2
                                
                                # 4. 模拟真实鼠标行为
                                page.mouse.move(x, y)           # 移动到目标位置
                                page.wait_for_timeout(200)      # 短暂停留，模拟人类反应
                                page.mouse.click(x, y)          # 单击
                                page.wait_for_timeout(300)      # 等待响应
                                
                                return True
                            except Exception as e:
                                log(f"鼠标点击失败: {e}")
                                return False

                        # B站专用播放按钮选择器（按优先级排序）
                        bilibili_play_selectors = [
                            '.bpx-player-ctrl-play',                    # B站主播放按钮
                            '.bpx-player-ctrl-play-icon',               # B站播放图标
                            '.bpx-player-ctrl-play-btn',                # B站播放按钮
                            '.bpx-player-sending-area',                 # B站播放区域
                            '.bpx-player-ctrl-play-icon-wrapper',       # B站播放图标包装器
                            '.bpx-player-ctrl-play-icon-container',     # B站播放图标容器
                            '.play-button',                             # 通用播放按钮
                            '.play-btn',                                # 通用播放按钮
                            'button[title*="播放"]',                    # 带播放文字的按钮
                            'button[aria-label*="播放"]',               # 无障碍标签
                            "[class*='play'][class*='btn']",            # 包含play和btn的类名
                            "[class*='play'][class*='icon']",           # 包含play和icon的类名
                        ]

                        clicked = False

                        # 1) 主页面内尝试点击播放按钮
                        log("尝试在主页面点击播放按钮")
                        for sel in bilibili_play_selectors:
                            try:
                                loc = page.locator(sel).first
                                if loc.is_visible(timeout=1500):
                                    log(f"找到播放按钮: {sel}")
                                    if click_with_mouse_on_locator(loc):
                                        log(f"光标点击播放按钮成功: {sel}")
                                        clicked = True
                                        break
                            except Exception as e:
                                log(f"尝试选择器 {sel} 失败: {e}")
                                continue

                        # 2) iframe内尝试（B站可能使用iframe）
                        if not clicked:
                            log("尝试在iframe内点击播放按钮")
                            try:
                                for frame in page.frames:
                                    if clicked:
                                        break
                                    for sel in bilibili_play_selectors:
                                        try:
                                            loc = frame.locator(sel).first
                                            if loc.is_visible(timeout=1500):
                                                log(f"在iframe中找到播放按钮: {sel}")
                                                if click_with_mouse_on_locator(loc):
                                                    log(f"在iframe内光标点击播放按钮成功: {sel}")
                                                    clicked = True
                                                    break
                                        except Exception as e:
                                            log(f"iframe内尝试选择器 {sel} 失败: {e}")
                                            continue
                            except Exception as e:
                                log(f"iframe操作失败: {e}")

                        # 3) 退而求其次：点击播放器容器中心
                        if not clicked:
                            log("尝试点击播放器容器中心")
                            container_selectors = [
                                '.bpx-player-container',                # B站播放器容器
                                '.bilibili-player',                     # B站播放器
                                '.video-player',                        # 通用视频播放器
                                "[class*='player']",                    # 包含player的类名
                                "[class*='video']"                      # 包含video的类名
                            ]
                            
                            for sel in container_selectors:
                                try:
                                    loc = page.locator(sel).first
                                    if loc.is_visible(timeout=1500):
                                        log(f"找到播放器容器: {sel}")
                                        if click_with_mouse_on_locator(loc):
                                            log(f"光标点击播放器容器成功: {sel}")
                                            clicked = True
                                            break
                                except Exception as e:
                                    log(f"尝试容器选择器 {sel} 失败: {e}")
                                    continue

                        if clicked:
                            log("光标点击播放流程完成")
                        else:
                            log("光标点击未找到可操作目标")

                    except Exception as e:
                        log(f"光标点击播放失败: {e}")
                elif action == 'video_keyboard_play':
                    # 使用Playwright键盘事件
                    log("使用Playwright键盘播放")
                    try:
                        # 先聚焦到视频元素
                        video_selectors = [
                            'video',
                            '.bpx-player-container',
                            '.bilibili-player',
                            '.video-player'
                        ]
                        
                        focused = False
                        for selector in video_selectors:
                            try:
                                page.wait_for_selector(selector, timeout=2000)
                                page.focus(selector)
                                log(f"聚焦到视频元素: {selector}")
                                focused = True
                                break
                            except Exception:
                                continue
                        
                        if not focused:
                            # 如果没找到视频元素，聚焦到页面主体
                            page.focus('body')
                            log("聚焦到页面主体")
                        
                        # 发送键盘事件
                        keyboard_keys = ['Space', 'Enter', 'ArrowRight']
                        for key in keyboard_keys:
                            try:
                                page.keyboard.press(key)
                                log(f"按下键盘: {key}")
                                import time
                                time.sleep(0.5)  # 短暂等待
                            except Exception as e:
                                log(f"键盘事件失败 {key}: {e}")
                        
                        log("键盘播放完成")
                    except Exception as e:
                        log(f"键盘播放失败: {e}")
                else:
                    log(f"未知动作: {action}")

            title = page.title()
            current_url = page.url
            # 如果需要保持页面打开，则在此等待指定时间
            try:
                if keep_open_ms and keep_open_ms > 0:
                    log(f"保持页面打开 {keep_open_ms}ms")
                    page.wait_for_timeout(keep_open_ms)
            finally:
                browser.close()

        return {
            "success": True,
            "title": title,
            "current_url": current_url,
            "logs": logs,
        }
    except Exception as e:
        logger.error(f"自动化失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "logs": logs,
        }


def automate_bilibili_search_and_play(keyword: str) -> Dict[str, Any]:
    """在B站搜索关键词并使用光标点击视频进行播放
    
    操作流程：
    1. 打开B站首页
    2. 在搜索框输入关键词
    3. 点击搜索按钮或按回车
    4. 等待搜索结果加载
    5. 使用光标点击第一个视频
    6. 等待视频页面加载
    7. 使用光标点击播放按钮
    """
    # 更鲁棒的选择器集合
    search_input_selectors = [
        "input#nav-searchform input",
        ".nav-search-input input",
        "input[type=search]",
        "input[placeholder*='搜索']",
        "input[placeholder*='搜']",
    ]
    search_click_helpers = [
        ".nav-search-input",
        ".nav-search-btn",
        ".nav-search-logo",
        "button:has-text('搜索')",
    ]
    result_card_selectors = [
        "a[href*='/video/']",
        ".bili-video-card a",
        ".video-item a",
        ".video-card a",
    ]

    up_tab_selectors = [
        "text=用户",
        "text=UP主",
        "role=tab[name='用户']",
        "role=tab[name='UP主']",
        "[role=tab]:has-text('用户')",
        "[role=tab]:has-text('UP主')",
    ]

    up_card_selectors = [
        "a[href*='/space/']:has-text('影视飓风')",
        "[data-ct*='user'] a:has-text('影视飓风')",
        "a:has(.bili-user-card__info:has-text('影视飓风'))",
        "a:has-text('影视飓风')",
    ]

    up_video_tab_selectors = [
        "text=视频",
        "[role=tab]:has-text('视频')",
        "a[href*='/video?']",
    ]

    up_first_video_selectors = [
        ".bili-video-card a",
        ".video-card a",
        "a[href*='/video/']",
    ]

    steps: List[Dict[str, Any]] = [
        {"action": "sleep", "ms": 2500},
        # 尝试关闭各类弹窗/遮罩（可选）
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 600},
        # 先尝试使用全局'/'快捷键激活搜索
        {"action": "press_global", "key": "/"},
        {"action": "sleep", "ms": 300},
        # 若未激活，再尝试点击搜索区域与输入框
        {"action": "click", "selector": ", ".join(search_click_helpers), "optional": True},
        {"action": "sleep", "ms": 200},
        {"action": "click", "selector": ", ".join(search_input_selectors), "optional": True},
        {"action": "sleep", "ms": 300},
        # 使用键盘全局输入关键词（即使未成功聚焦也尽量输入）
        {"action": "keyboard_type", "text": keyword, "delay": 20},
        {"action": "sleep", "ms": 400},
        # 回车触发搜索（全局）
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 2800},
        # 仅等待并进入 用户/UP主 路径
        {"action": "wait_any", "selectors": up_tab_selectors, "timeout": 20000},
        {"action": "sleep", "ms": 900},
        {"action": "click_any", "selectors": up_tab_selectors},
        {"action": "sleep", "ms": 600},
        {"action": "click_any", "selectors": up_card_selectors, "new_page": True},
        {"action": "sleep", "ms": 1800},
        # 进入该UP的“视频”标签
        {"action": "click_any", "selectors": up_video_tab_selectors, "optional": True},
        {"action": "sleep", "ms": 1200},
        # 在UP主页点击第一个视频
        {"action": "click_any", "selectors": up_first_video_selectors, "new_page": True},
        {"action": "wait_url", "includes": "/video/", "timeout": 20000},
        # 校验作者名为“影视飓风”（尽量，但不阻断）
        {"action": "wait_any", "selectors": [
            "a[href*='/space/']:has-text('影视飓风')",
            "[class*='up'] a:has-text('影视飓风')",
            "text=影视飓风"
        ], "timeout": 8000, "optional": True},
        {"action": "sleep", "ms": 3000},
        # 等待播放器
        {"action": "wait_video_ready", "timeout": 20000},
        {"action": "sleep", "ms": 1500},
        # 光标点击播放
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 2000},
        # 兜底
        {"action": "video_play"},
        {"action": "sleep", "ms": 1200},
    ]
    # 提高整体超时时间，降低页面关闭/等待超时风险
    return automate_page("https://www.bilibili.com", steps, headless=False, timeout_ms=45000)


def generic_site_search(
    url: str,
    keyword: str,
    click_first_result: bool = True,
    headless: Optional[bool] = None,
    timeout_ms: int = 20000,
) -> Dict[str, Any]:
    """在任意站点执行站内搜索并可选点击第一个结果。

    - 自动尝试多组常见搜索框选择器
    - 回车提交后等待出现结果链接或按钮
    - 可选点击第一个结果
    """
    search_selectors = get_search_selectors()
    result_link_selectors = get_result_link_selectors()

    steps: List[Dict[str, Any]] = [
        {"action": "sleep", "ms": 600},
        {"action": "click", "selector": ", ".join(search_selectors)},
        {"action": "type", "selector": ", ".join(search_selectors), "text": keyword, "clear": True},
        {"action": "press", "selector": ", ".join(search_selectors), "key": "Enter"},
        {"action": "wait", "selector": ", ".join(result_link_selectors), "state": "visible"},
        {"action": "sleep", "ms": 600},
    ]
    if click_first_result:
        steps += [
            {"action": "click", "selector": ", ".join(result_link_selectors)},
            {"action": "wait", "selector": "a, button, video", "state": "visible"},
        ]

    return automate_page(url=url, steps=steps, headless=headless, timeout_ms=timeout_ms)


def generic_browse_product(
    url: str,
    keyword: str,
    match_text: Optional[str] = None,
    headless: Optional[bool] = None,
    timeout_ms: int = 20000,
) -> Dict[str, Any]:
    """通用商品浏览：搜索关键词后，按匹配文本点击商品；若无匹配文本，仅停留在结果页。"""
    # 先只做站内搜索，不默认点击
    _ = generic_site_search(url=url, keyword=keyword, click_first_result=False, headless=headless, timeout_ms=timeout_ms)
    if match_text and match_text.strip():
        sel = f"a:has-text('{match_text.strip()}')"
        steps: List[Dict[str, Any]] = [
            {"action": "wait", "selector": sel, "state": "visible", "optional": True},
            {"action": "click", "selector": sel},
            {"action": "wait", "selector": "a, button, [role=button]", "state": "visible", "optional": True},
            {"action": "sleep", "ms": 600},
        ]
        return automate_page(url=url, steps=steps, headless=headless, timeout_ms=timeout_ms)
    return {"success": True, "title": "已展示搜索结果", "current_url": url, "logs": ["已完成站内搜索，未点击具体商品（缺少匹配文本）"]}


def generic_play_video(
    url: str,
    keyword: str,
    match_text: Optional[str] = None,
    headless: Optional[bool] = None,
    timeout_ms: int = 20000,
) -> Dict[str, Any]:
    """通用视频播放：搜索关键词后，根据匹配文本点击视频；若无匹配文本，仅停留在结果页。"""
    _ = generic_site_search(url=url, keyword=keyword, click_first_result=False, headless=headless, timeout_ms=timeout_ms)
    if match_text and match_text.strip():
        video_sel = f"a:has-text('{match_text.strip()}'), ytd-video-renderer:has-text('{match_text.strip()}') a#thumbnail"
        steps: List[Dict[str, Any]] = [
            {"action": "wait", "selector": video_sel, "state": "visible", "optional": True},
            {"action": "click", "selector": video_sel},
            {"action": "wait", "selector": "video", "state": "visible", "optional": True},
            {"action": "sleep", "ms": 800},
        ]
        return automate_page(url=url, steps=steps, headless=headless, timeout_ms=timeout_ms)
    return {"success": True, "title": "已展示搜索结果", "current_url": url, "logs": ["已完成站内搜索，未点击具体视频（缺少匹配文本）"]}


def generic_add_to_cart(
    url: str,
    keyword: str,
    match_text: Optional[str] = None,
    headless: Optional[bool] = None,
    timeout_ms: int = 20000,
) -> Dict[str, Any]:
    """通用加购：搜索关键词后，按匹配文本进入商品并尝试点击加入购物车；若无匹配文本，仅停留在结果页。"""
    add_btn_selectors = get_add_to_cart_selectors()
    # 先站内搜索
    _ = generic_site_search(url=url, keyword=keyword, click_first_result=False, headless=headless, timeout_ms=timeout_ms)
    if match_text and match_text.strip():
        product_sel = f"a:has-text('{match_text.strip()}')"
        steps: List[Dict[str, Any]] = [
            {"action": "wait", "selector": product_sel, "state": "visible", "optional": True},
            {"action": "click", "selector": product_sel},
            {"action": "wait", "selector": ", ".join(add_btn_selectors), "state": "visible", "optional": True},
            {"action": "click", "selector": ", ".join(add_btn_selectors)},
            {"action": "sleep", "ms": 600},
        ]
        return automate_page(url=url, steps=steps, headless=headless, timeout_ms=timeout_ms)
    return {"success": True, "title": "已展示搜索结果", "current_url": url, "logs": ["已完成站内搜索，未加购（缺少匹配文本）"]}
