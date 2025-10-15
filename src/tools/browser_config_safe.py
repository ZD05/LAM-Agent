"""
安全浏览器配置模块
修复可能导致黑屏的浏览器参数
"""
from typing import Dict, Any, List, Optional
from src.config import settings
import os


def get_safe_browser_args() -> List[str]:
    """获取安全的浏览器启动参数，避免黑屏问题"""
    return [
        # 基本安全参数
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        
        # 修复显示问题
        '--disable-gpu',  # 禁用GPU加速，避免与Steam冲突
        '--disable-software-rasterizer',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        
        # 反爬虫破解措施（保留必要的）
        '--disable-blink-features=AutomationControlled',
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
        '--disable-field-trial-config',
        '--disable-ipc-flooding-protection',
        
        # 模拟真实浏览器环境
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        '--accept-language=zh-CN,zh;q=0.9,en;q=0.8',
        '--accept-encoding=gzip, deflate, br',
        
        # 支持iframe和嵌入播放器
        '--allow-running-insecure-content',
        
        # 移除可能导致问题的GPU相关参数
        # '--enable-features=VaapiVideoDecoder',  # 移除
        # '--enable-accelerated-video-decode',    # 移除
        # '--enable-hardware-overlays',           # 移除
        # '--enable-gpu-rasterization',           # 移除
        # '--enable-zero-copy'                    # 移除
    ]


def get_safe_browser_context_config() -> Dict[str, Any]:
    """获取安全的浏览器上下文配置 - 适配已登录状态"""
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
        
        # 模拟真实用户环境（已登录状态）
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
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        },
        
        # 保持登录状态相关配置
        'storage_state': None,  # 可以设置存储状态来保持登录
        'record_video_dir': None,  # 不录制视频，提高性能
        'record_har_path': None,  # 不记录HAR，提高性能
    }


def get_launch_kwargs(headless: Optional[bool] = None) -> Dict[str, Any]:
    """统一的浏览器启动参数，默认使用系统 Edge。

    优先级：
    1) settings.lam_browser_executable 如果设置，则使用 executable_path
    2) 否则使用 settings.lam_browser_channel（默认 msedge）
    """
    kwargs: Dict[str, Any] = {
        "headless": settings.lam_browser_headless if headless is None else headless,
        "args": get_safe_browser_args(),
    }

    if settings.lam_browser_executable:
        kwargs["executable_path"] = settings.lam_browser_executable
    else:
        kwargs["channel"] = settings.lam_browser_channel or "msedge"

    # 代理（如果存在）
    proxy = get_proxy_config()
    if proxy:
        kwargs["proxy"] = proxy

    return kwargs


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
        "input[name=pwd]",
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
    """从环境变量读取代理设置"""
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    server = https_proxy or http_proxy
    if server:
        return {"server": server}
    return None


