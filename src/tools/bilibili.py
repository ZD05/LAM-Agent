from typing import Dict, Any, List, Optional
import os
import unicodedata

from .browser import automate_page
def _normalize_text(text: str) -> str:
    """对中文等Unicode文本进行标准化，降低终端/平台编码差异导致的显示异常。"""
    try:
        return unicodedata.normalize('NFC', text)
    except Exception:
        return text

# 强制UTF-8输出以减少控制台乱码（不影响浏览器内真实输入）
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')


# 选择器配置（尽量保持与站点结构解耦，按优先级排列）
SEARCH_INPUT_SELECTORS: List[str] = [
    "#nav-searchform input",
    ".nav-search-input input",
    "input[type='search']",
    "input[placeholder*='搜索']",
    "input[placeholder*='搜']",
    "input[name='search_keyword']",
    ".nav-search .search-input input",
    "#search-input",
    ".search-input input",
]

SEARCH_CLICK_HELPERS: List[str] = [
    ".nav-search-input",
    ".nav-search-btn",
    ".nav-search-logo",
    "button:has-text('搜索')",
    ".nav-search",
    "#nav-searchform",
]

UP_TAB_SELECTORS: List[str] = [
    "text=用户",
    "text=UP主",
    "role=tab[name='用户']",
    "role=tab[name='UP主']",
    "[role=tab]:has-text('用户')",
    "[role=tab]:has-text('UP主')",
]

UP_CARD_SELECTORS: List[str] = [
    # Account anchors constrained by visible author name
    "a.user-name[href^='//space.bilibili.com']:has-text('影视飓风')",
    "a.user-name[href*='space.bilibili.com']:has-text('影视飓风')",
    # Generic fallbacks constrained by text
    "a[href*='/space/']:has-text('影视飓风')",
    "[data-ct*='user'] a:has-text('影视飓风')",
    "a:has(.bili-user-card__info:has-text('影视飓风'))",
    # Video card owner region → author link (by text)
    ".bili-video-card__info--owner a[href^='//space.bilibili.com']",
    "a[href^='//space.bilibili.com']:has(.bili-video-card__info--author:has-text('影视飓风'))",
    ".bili-video-card__info--owner:has-text('影视飓风') a[href^='//space.bilibili.com']",
]

UP_VIDEO_TAB_SELECTORS: List[str] = [
    "text=视频",
    "[role=tab]:has-text('视频')",
    "a[href*='/video?']",
]

RESULT_VIDEO_SELECTORS: List[str] = [
    "a[href*='/video/']",
    ".bili-video-card a",
    ".video-item a",
    ".video-card a",
]

UP_FIRST_VIDEO_SELECTORS: List[str] = [
    ".bili-video-card a",
    ".video-card a",
    "a[href*='/video/']",
]


def search_up_and_open(up_name: str, *, timeout_ms: int = 45000, keep_open_ms: int | None = None) -> Dict[str, Any]:
    up_name = _normalize_text(up_name)
    steps: List[Dict[str, Any]] = [
        {"action": "sleep", "ms": 2500},
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 600},
        {"action": "click", "selector": ", ".join(SEARCH_CLICK_HELPERS), "optional": True},
        {"action": "sleep", "ms": 200},
        {"action": "click", "selector": ", ".join(SEARCH_INPUT_SELECTORS), "optional": True},
        {"action": "sleep", "ms": 200},
        {"action": "press_global", "key": "Control+A"},
        {"action": "sleep", "ms": 120},
        {"action": "press_global", "key": "Backspace"},
        {"action": "sleep", "ms": 150},
        {"action": "keyboard_type", "text": up_name, "delay": 20},
        {"action": "sleep", "ms": 250},
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 3000},
        # 先进入“用户/UP主”标签（可选，适当延长等待）
        {"action": "wait_any", "selectors": UP_TAB_SELECTORS, "timeout": 20000, "optional": True},
        {"action": "sleep", "ms": 300},
        {"action": "click_any", "selectors": UP_TAB_SELECTORS, "optional": True},
        {"action": "sleep", "ms": 900},
        # 触发懒加载：向下滚动几次
        {"action": "evaluate", "script": "window.scrollBy(0, 600)"},
        {"action": "sleep", "ms": 300},
        {"action": "evaluate", "script": "window.scrollBy(0, 900)"},
        {"action": "sleep", "ms": 300},
        {"action": "evaluate", "script": "window.scrollBy(0, 1200)"},
        {"action": "sleep", "ms": 400},
        {"action": "evaluate", "script": "window.scrollBy(0, 1400)"},
        {"action": "sleep", "ms": 500},
        {"action": "evaluate", "script": "window.scrollBy(0, 1600)"},
        {"action": "sleep", "ms": 600},
        # 使用“关注”关键词定位用户卡片，再点击旁边账号名称（受昵称与 space 域约束）
        {"action": "wait_any", "selectors": [
            # 卡片内同时包含昵称与“关注”按钮/文本，并包含用户名链接
            f".bili-user-item:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f".bili-user-item:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f".bili-user-item:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f".bili-user-item:has-text('{up_name}'):has(button:has-text('关注')) a[href*='space.bilibili.com']",
            f".user-item:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f".user-item:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f".user-item:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f".user-item:has-text('{up_name}'):has(button:has-text('关注')) a[href*='space.bilibili.com']",
            f".user-card:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f".user-card:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f".user-card:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f"[class*='user']:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f"[class*='user']:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f"[class*='user']:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f"li:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            # 兼容：纯文本“关注”
            f".bili-user-item:has-text('{up_name}'):has-text('关注') a.user-name",
            f".user-item:has-text('{up_name}'):has-text('关注') a.user-name",
            f".user-card:has-text('{up_name}'):has-text('关注') a.user-name",
            f"[class*='user']:has-text('{up_name}'):has-text('关注') a.user-name",
        ], "timeout": 15000, "optional": True},
        {"action": "sleep", "ms": 300},
        {"action": "click_any", "selectors": [
            f".bili-user-item:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f".bili-user-item:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f".bili-user-item:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f".bili-user-item:has-text('{up_name}'):has(button:has-text('关注')) a[href*='space.bilibili.com']",
            f".user-item:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f".user-item:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f".user-item:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f".user-item:has-text('{up_name}'):has(button:has-text('关注')) a[href*='space.bilibili.com']",
            f".user-card:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f".user-card:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f".user-card:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f"[class*='user']:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            f"[class*='user']:has-text('{up_name}'):has([class*='follow']) a.user-name",
            f"[class*='user']:has-text('{up_name}'):has(.follow-btn, .be-btn, .btn-follow) a.user-name",
            f"li:has-text('{up_name}'):has(button:has-text('关注')) a.user-name",
            # 兼容：纯文本“关注”
            f".bili-user-item:has-text('{up_name}'):has-text('关注') a.user-name",
            f".user-item:has-text('{up_name}'):has-text('关注') a.user-name",
            f".user-card:has-text('{up_name}'):has-text('关注') a.user-name",
            f"[class*='user']:has-text('{up_name}'):has-text('关注') a.user-name",
            f"li:has-text('{up_name}'):has-text('关注') a.user-name",
        ], "new_page": True, "optional": True},
        {"action": "sleep", "ms": 800},
        # 在用户结果中等待并点击目标账号（仅按作者昵称与 space 域名约束，不用 MID）
        {"action": "wait_any", "selectors": [
            f"a.user-name[href^='//space.bilibili.com']:has-text('{up_name}')",
            f"a.user-name[href*='space.bilibili.com']:has-text('{up_name}')",
            f".bili-video-card__info--owner:has-text('{up_name}') a[href^='//space.bilibili.com']",
            f"a[href^='//space.bilibili.com']:has(.bili-video-card__info--author:has-text('{up_name}'))",
            f"a[href*='/space/']:has-text('{up_name}')",
        ], "timeout": 10000},
        {"action": "sleep", "ms": 400},
        {"action": "click_any", "selectors": [
            f"a.user-name[href^='//space.bilibili.com']:has-text('{up_name}')",
            f"a.user-name[href*='space.bilibili.com']:has-text('{up_name}')",
            f".bili-video-card__info--owner:has-text('{up_name}') a[href^='//space.bilibili.com']",
            f"a[href^='//space.bilibili.com']:has(.bili-video-card__info--author:has-text('{up_name}'))",
            f"a[href*='/space/']:has-text('{up_name}')",
        ], "new_page": True},
        # 校验：落页为 B 站空间域名，且页面包含作者昵称（不使用 MID）
        {"action": "wait_url", "includes": "space.bilibili.com", "timeout": 15000},
        {"action": "wait_any", "selectors": [
            f"text={up_name}",
            f".h-name:has-text('{up_name}')",
            f".info:has-text('{up_name}')",
            f"a:has-text('{up_name}')",
        ], "timeout": 12000, "optional": True},
        {"action": "sleep", "ms": 2000},
    ]
    return automate_page("https://www.bilibili.com", steps, headless=False, timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)


def play_first_video_from_up(*, timeout_ms: int = 45000, keep_open_ms: int | None = None) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = [
        {"action": "click_any", "selectors": UP_VIDEO_TAB_SELECTORS, "optional": True},
        {"action": "sleep", "ms": 1200},
        {"action": "click_any", "selectors": UP_FIRST_VIDEO_SELECTORS, "new_page": True},
        {"action": "wait_url", "includes": "/video/", "timeout": 20000},
        {"action": "sleep", "ms": 3000},
        {"action": "wait_video_ready", "timeout": 20000},
        {"action": "sleep", "ms": 1500},
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 2000},
        {"action": "video_play"},
        {"action": "sleep", "ms": 1200},
    ]
    # 继续在当前已是UP主页的上下文中执行
    return automate_page("https://www.bilibili.com", steps, headless=False, timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)


def search_and_play_first_video_strict(up_name: str = "影视飓风", *, timeout_ms: int = 45000, keep_open_ms: int | None = None) -> Dict[str, Any]:
    """严格走UP主页：搜索→UP标签→进入UP主页→视频→第一个视频→播放。"""
    _ = search_up_and_open(up_name, timeout_ms=timeout_ms, keep_open_ms=None)
    return play_first_video_from_up(timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)


def open_up_homepage(up_name: str = "影视飓风", *, timeout_ms: int = 45000, keep_open_ms: int | None = 60000) -> Dict[str, Any]:
    """只打开指定UP主的主页，不进行播放。默认保持页面开启60秒。"""
    return search_up_and_open(up_name, timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)


def search_click_account_play_first(
    up_name: str = "影视飓风",
    *,
    wait_ms: int = 10000,
    timeout_ms: int = 45000,
    keep_open_ms: int | None = 60000,
) -> Dict[str, Any]:
    """使用Bing搜索B站→进入B站→搜索UP主→点击账号卡片进入主页→停顿→点击第一个视频播放。"""
    up_name = _normalize_text(up_name)

    # 使用Bing搜索B站
    search_url = "https://www.bing.com/search?q=bilibili.com"
    
    # Bing搜索结果中的B站官网链接选择器（优先选择官网链接）
    bilibili_link_selectors = [
        "a[href='https://www.bilibili.com/']",
        "a[href='https://bilibili.com/']",
        ".b_algo a[href='https://www.bilibili.com/']",
        ".b_title a[href='https://www.bilibili.com/']",
        "a[href*='bilibili.com']:not([href*='image']):not([href*='img']):not([href*='photo'])",
        ".b_algo a[href*='bilibili.com']:not([href*='image']):not([href*='img'])",
        ".b_title a[href*='bilibili.com']:not([href*='image']):not([href*='img'])",
    ]

    steps: List[Dict[str, Any]] = [
        {"action": "sleep", "ms": 2500},
        # 关闭Bing弹窗
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .b_modal, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 1000},
        # 等待Bing搜索结果中的B站链接出现
        {"action": "wait_any", "selectors": bilibili_link_selectors, "timeout": 20000},
        {"action": "sleep", "ms": 1000},
        # 点击B站链接进入主页
        {"action": "click_any", "selectors": bilibili_link_selectors, "new_page": True},
        {"action": "sleep", "ms": 3000},
        # 关闭B站弹窗
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 1000},
        # 在B站内搜索UP主（容器→输入框→清空→输入→回车）
        {"action": "click", "selector": ", ".join(SEARCH_CLICK_HELPERS), "optional": True},
        {"action": "sleep", "ms": 200},
        {"action": "click", "selector": ", ".join(SEARCH_INPUT_SELECTORS), "optional": True},
        {"action": "sleep", "ms": 200},
        {"action": "press_global", "key": "Control+A"},
        {"action": "sleep", "ms": 120},
        {"action": "press_global", "key": "Backspace"},
        {"action": "sleep", "ms": 150},
        {"action": "keyboard_type", "text": up_name, "delay": 50},
        {"action": "sleep", "ms": 250},
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 2000},
        # 等待出现UP主标签或账号卡片（优先等待精确账号链接）
        {"action": "wait_any", "selectors": [
            "a.user-name[href^='//space.bilibili.com/946974']",
        ] + UP_TAB_SELECTORS + [s.replace('影视飓风', up_name) for s in UP_CARD_SELECTORS], "timeout": 30000},
        {"action": "sleep", "ms": 600},
        # 点击“用户/UP主”标签（若存在）
        {"action": "click_any", "selectors": UP_TAB_SELECTORS, "optional": True},
        {"action": "sleep", "ms": 800},
        # 点击精确账号链接进入主页
        {"action": "click_any", "selectors": [
            "a.user-name[href^='//space.bilibili.com/946974']",
            f"a.user-name[href^='//space.bilibili.com']:has-text('{up_name}')",
            f"a.user-name[href*='space.bilibili.com']:has-text('{up_name}')",
            f"a[href*='/space/']:has-text('{up_name}')",
        ], "new_page": True},
        {"action": "sleep", "ms": 3000},
        # 在UP主主页点击第一个视频
        {"action": "wait_any", "selectors": UP_FIRST_VIDEO_SELECTORS, "timeout": 20000},
        {"action": "sleep", "ms": 800},
        {"action": "click_any", "selectors": UP_FIRST_VIDEO_SELECTORS, "new_page": True},
        {"action": "wait_url", "includes": "/video/", "timeout": 20000},
        {"action": "sleep", "ms": 3000},
        {"action": "wait_video_ready", "timeout": 20000},
        {"action": "sleep", "ms": 1200},
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 1200},
        {"action": "video_play"},
        {"action": "sleep", "ms": 1000},
    ]
    return automate_page(search_url, steps, headless=False, timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)


def click_edge_taskbar_and_play_video(
    up_name: str = "影视飓风",
    *,
    wait_ms: int = 10000,
    timeout_ms: int = 45000,
    keep_open_ms: int | None = 60000,
) -> Dict[str, Any]:
    """点击任务栏Edge图标→打开搜索引擎→搜索B站→播放影视飓风视频"""
    up_name = _normalize_text(up_name)
    
    # 使用pyautogui点击任务栏Edge图标
    try:
        import pyautogui
        import time
        
        # 设置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # 点击任务栏Edge图标（通常在左下角）
        # 这里需要根据实际屏幕分辨率调整坐标
        edge_icon_x, edge_icon_y = 50, 1050  # 示例坐标，需要根据实际情况调整
        
        print(f"Clicking Edge icon at ({edge_icon_x}, {edge_icon_y})")
        pyautogui.click(edge_icon_x, edge_icon_y)
        time.sleep(3)
        
        # 现在Edge应该已经打开了，直接导航到Bing
        steps: List[Dict[str, Any]] = [
            {"action": "sleep", "ms": 2000},
            # 导航到Bing
            {"action": "goto", "url": "https://www.bing.com"},
            {"action": "sleep", "ms": 2000},
            # 在Bing中搜索B站
            {"action": "click", "selector": "input[name='q'], input#sb_form_q, input[type='search']"},
            {"action": "sleep", "ms": 500},
            {"action": "type", "selector": "input[name='q'], input#sb_form_q, input[type='search']", "text": "bilibili.com", "clear": True},
            {"action": "sleep", "ms": 500},
            {"action": "press", "selector": "input[name='q'], input#sb_form_q, input[type='search']", "key": "Enter"},
            {"action": "sleep", "ms": 3000},
            # 点击B站官网链接
            {"action": "click_any", "selectors": [
                "a[href='https://www.bilibili.com/']",
                "a[href='https://bilibili.com/']",
                ".b_algo a[href*='bilibili.com']",
            ], "new_page": True},
            {"action": "sleep", "ms": 3000},
            # 关闭B站弹窗
            {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
            {"action": "sleep", "ms": 1000},
            # 在B站内搜索UP主
            {"action": "click", "selector": "input[type='search'], input[placeholder*='搜索'], .nav-search-input input, #nav-searchform input", "optional": True},
            {"action": "sleep", "ms": 500},
            {"action": "keyboard_type", "text": up_name, "delay": 50},
            {"action": "sleep", "ms": 500},
            {"action": "press_global", "key": "Enter"},
            {"action": "sleep", "ms": 3000},
            # 等待搜索结果出现
            {"action": "wait_any", "selectors": [
                ".up-item",
                ".user-item", 
                ".result-item",
                ".bili-user-item",
                ".user-card",
                ".up-card",
                ".search-result",
                ".bili-video-card",
                ".video-item",
            ], "timeout": 20000},
            {"action": "sleep", "ms": 2000},
            # 查找并点击UP主账号链接（优先选择包含space链接的）
            {"action": "click_any", "selectors": [
                f"a.user-name[href^='//space.bilibili.com']:has-text('{up_name}')",
                f"a.user-name[href*='space.bilibili.com']:has-text('{up_name}')",
                f"a[href*='/space/']:has-text('{up_name}')",
                f"a[href*='space.bilibili.com']:has-text('{up_name}')",
                f".up-item:has-text('{up_name}') a[href*='/space/']",
                f".user-item:has-text('{up_name}') a[href*='/space/']",
                f".result-item:has-text('{up_name}') a[href*='/space/']",
                f".bili-user-item:has-text('{up_name}') a[href*='/space/']",
                f".user-card:has-text('{up_name}') a[href*='/space/']",
                f".up-card:has-text('{up_name}') a[href*='/space/']",
                f".search-result:has-text('{up_name}') a[href*='/space/']",
            ], "new_page": True, "optional": True},
            {"action": "sleep", "ms": 1000},
            # 如果上面的选择器都失败，尝试点击包含UP主名称的文本
            {"action": "click", "selector": f"text={up_name}", "optional": True},
            {"action": "sleep", "ms": 1000},
            {"action": "sleep", "ms": 3000},
            # 在UP主主页点击第一个视频
            {"action": "wait_any", "selectors": [
                ".video-item a",
                ".bili-video-card a", 
                ".video-card a",
                "[class*='video'] a",
                "a[href*='/video/']",
                ".bili-video-item a",
                ".video-list a",
                ".space-video-list a[href*='/video/']",
                ".small-item a",
                ".video-list-item a",
                ".bili-video-item a",
                ".video-card-wrap a",
                ".video-item-wrap a",
                "a[href*='bilibili.com/video/']",
                ".space-video-list .small-item a",
                ".video-list .small-item a",
                ".video-list .video-item a",
            ], "timeout": 20000},
            {"action": "sleep", "ms": 1000},
            {"action": "click_any", "selectors": [
                ".video-item a",
                ".bili-video-card a", 
                ".video-card a",
                "[class*='video'] a",
                "a[href*='/video/']",
                ".bili-video-item a",
                ".video-list a",
                ".space-video-list a[href*='/video/']",
                ".small-item a",
                ".video-list-item a",
                ".bili-video-item a",
                ".video-card-wrap a",
                ".video-item-wrap a",
                "a[href*='bilibili.com/video/']",
                ".space-video-list .small-item a",
                ".video-list .small-item a",
                ".video-list .video-item a",
            ], "new_page": True},
            {"action": "sleep", "ms": 5000},
            # 等待视频加载完成
            {"action": "wait_video_ready", "timeout": 15000},
            {"action": "sleep", "ms": 2000},
            # 等待指定时长
            {"action": "sleep", "ms": max(0, int(wait_ms))},
            {"action": "sleep", "ms": 1500},
            {"action": "video_click_play"},
            {"action": "sleep", "ms": 2000},
            {"action": "video_play"},
            {"action": "sleep", "ms": 1200},
        ]
        
        # 使用一个简单的URL作为起始点，实际会通过pyautogui点击任务栏
        return automate_page("about:blank", steps, headless=False, timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)
        
    except ImportError:
        # 如果没有pyautogui，回退到原来的方法
        logger.warning("pyautogui not available, falling back to direct browser method")
        return search_click_account_play_first(up_name, wait_ms=wait_ms, timeout_ms=timeout_ms, keep_open_ms=keep_open_ms)


