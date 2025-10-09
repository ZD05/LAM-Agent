"""
浏览器配置模块
统一管理 Playwright 浏览器配置，减少代码重复
"""
from typing import Dict, Any, List, Optional
import os


def get_browser_args() -> List[str]:
    """获取浏览器启动参数"""
    return [
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-gpu-sandbox',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--ignore-certificate-errors',
        '--ignore-ssl-errors',
        '--ignore-certificate-errors-spki-list',
        # 反爬虫破解措施
        '--disable-blink-features=AutomationControlled',
        '--disable-features=VizDisplayCompositor',
        '--disable-features=TranslateUI',
        '--disable-features=BlockInsecurePrivateNetworkRequests',
        '--disable-features=SameSiteByDefaultCookies',
        '--disable-features=MediaSessionService',
        '--disable-features=UserAgentClientHint',
        # 隐藏自动化特征
        '--disable-automation',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-default-apps',
        '--disable-sync',
        '--disable-translate',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-field-trial-config',
        '--disable-ipc-flooding-protection',
        # 模拟真实浏览器环境
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        '--accept-language=zh-CN,zh;q=0.9,en;q=0.8',
        '--accept-encoding=gzip, deflate, br',
        # 支持iframe和嵌入播放器
        '--allow-running-insecure-content',
        # 支持B站播放器
        '--enable-features=VaapiVideoDecoder',
        '--enable-accelerated-video-decode',
        '--enable-hardware-overlays',
        # Edge浏览器特定设置
        '--enable-edge-features',
        '--edge-experimental-features',
        '--enable-gpu-rasterization',
        '--enable-zero-copy'
    ]


def get_browser_context_config() -> Dict[str, Any]:
    """获取浏览器上下文配置"""
    return {
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        'viewport': {'width': 1920, 'height': 1080},
        'device_scale_factor': 1,
        'has_touch': False,
        'is_mobile': False,
        'locale': 'zh-CN',
        'timezone_id': 'Asia/Shanghai',
        'permissions': ['camera', 'microphone'],
        # 反爬虫破解配置
        'java_script_enabled': True,
        'bypass_csp': True,
        'ignore_https_errors': True,
        # 模拟真实用户环境
        'color_scheme': 'light',
        'reduced_motion': 'no-preference',
        'forced_colors': 'none',
        'extra_http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }


def get_video_play_selectors() -> List[str]:
    """获取视频播放按钮选择器列表"""
    return [
        # B站常见控件
        '.bpx-player-ctrl-play', '.bpx-player-ctrl-play-icon', '.bpx-player-ctrl-play-btn',
        '.bpx-player-sending-area', '.bpx-player-ctrl-play-icon-wrapper', '.bpx-player-ctrl-play-icon-container',
        # 通用
        '.play-button', '.play-btn', '.player-play', '.video-play',
        "[class*='play'][class*='btn']", "[class*='play'][class*='icon']",
        'button[title*="播放"]', 'button[aria-label*="播放"]'
    ]


def get_video_container_selectors() -> List[str]:
    """获取视频容器选择器列表"""
    return [
        '.bpx-player-container', '.bilibili-player', '.video-player',
        "[class*='player']", "[class*='video']"
    ]


def get_search_selectors() -> List[str]:
    """获取搜索框选择器列表"""
    return [
        "input[type=search]",
        "input[name=q]",
        "input[name=search]",
        "input#search",
        "input[aria-label='Search']",
        "input.s-input",
        "input.search-input",
        "input[name=keyword]",
        "input[name=wd]",
        "input[name=pwd]",  # 某些站点奇怪命名
        "input#nav-searchform input",
    ]


def get_result_link_selectors() -> List[str]:
    """获取结果链接选择器列表"""
    return [
        "a[href]",
        "a.result__a",
        "a#search-result",
        "ytd-video-renderer a#thumbnail",
        "a[href*='/video/']",
        "a[href*='item']",
        "a[href*='detail']",
    ]


def get_add_to_cart_selectors() -> List[str]:
    """获取加入购物车按钮选择器列表"""
    return [
        "button:has-text('加入购物车')",
        "#J_AddToCart",
        "button[aria-label*='Add to cart']",
        "button:has-text('加入購物車')",
        "button:has-text('Add to cart')",
    ]


def get_proxy_config() -> Optional[Dict[str, Any]]:
    """从环境变量读取代理设置，返回 Playwright 兼容的 proxy 配置。
    优先使用 HTTPS_PROXY，其次 HTTP_PROXY。示例：http://127.0.0.1:7890
    """
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    server = https_proxy or http_proxy
    if server:
        return {"server": server}
    return None


