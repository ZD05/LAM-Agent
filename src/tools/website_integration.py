#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import requests
import webbrowser
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from urllib.parse import urlparse, urljoin
import re

from .base_integration import BaseIntegration, ECommerceIntegration, VideoPlatformIntegration

logger = logging.getLogger(__name__)

class WebsiteIntegration:
    """通用网站集成类，提供网站访问和信息总结功能"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 常用网站配置
        self.website_configs = {
            'jd.com': {
                'name': '京东',
                'category': '电商',
                'search_url': 'https://search.jd.com/Search?keyword={keyword}',
                'homepage': 'https://www.jd.com',
                'special_handlers': ['jd_search_products', 'jd_get_product_info']
            },
            'taobao.com': {
                'name': '淘宝',
                'category': '电商',
                'search_url': 'https://s.taobao.com/search?q={keyword}',
                'homepage': 'https://www.taobao.com',
                'special_handlers': ['taobao_search_products', 'taobao_get_product_info']
            },
            'tmall.com': {
                'name': '天猫',
                'category': '电商',
                'search_url': 'https://list.tmall.com/search_product.htm?q={keyword}',
                'homepage': 'https://www.tmall.com',
                'special_handlers': ['tmall_search_products', 'tmall_get_product_info']
            },
            'amap.com': {
                'name': '高德地图',
                'category': '地图',
                'search_url': 'https://uri.amap.com/search?query={keyword}',
                'homepage': 'https://www.amap.com',
                'special_handlers': ['amap_search_location', 'amap_get_route']
            },
            'baidu.com': {
                'name': '百度',
                'category': '搜索',
                'search_url': 'https://www.baidu.com/s?wd={keyword}',
                'homepage': 'https://www.baidu.com',
                'special_handlers': ['baidu_search', 'baidu_get_news']
            },
            'zhihu.com': {
                'name': '知乎',
                'category': '问答',
                'search_url': 'https://www.zhihu.com/search?q={keyword}',
                'homepage': 'https://www.zhihu.com',
                'special_handlers': ['zhihu_search_questions', 'zhihu_get_answer']
            },
            'bilibili.com': {
                'name': '哔哩哔哩',
                'category': '视频',
                'search_url': 'https://search.bilibili.com/all?keyword={keyword}',
                'homepage': 'https://www.bilibili.com',
                'special_handlers': ['bilibili_search_videos', 'bilibili_get_video_info']
            },
            'pinduoduo.com': {
                'name': '拼多多',
                'category': '电商',
                'search_url': 'https://mobile.yangkeduo.com/search_result.html?search_key={keyword}',
                'homepage': 'https://www.pinduoduo.com',
                'special_handlers': ['pdd_search_products', 'pdd_get_product_info']
            },
            'douyin.com': {
                'name': '抖音',
                'category': '短视频',
                'search_url': 'https://www.douyin.com/search/{keyword}',
                'homepage': 'https://www.douyin.com',
                'special_handlers': ['douyin_search_videos', 'douyin_get_video_info']
            },
            'kuaishou.com': {
                'name': '快手',
                'category': '短视频',
                'search_url': 'https://www.kuaishou.com/search/video?searchKey={keyword}',
                'homepage': 'https://www.kuaishou.com',
                'special_handlers': ['kuaishou_search_videos', 'kuaishou_get_video_info']
            }
        }
    
    def open_website(self, url: str) -> Dict[str, Any]:
        """打开网站并检查自动登录"""
        try:
            # 标准化URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # 检查是否为已知网站
            domain = urlparse(url).netloc.lower()
            website_info = self._get_website_info(domain)
            
            # 使用浏览器自动化打开并检查登录
            try:
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
                        
                        return {
                            "success": True,
                            "message": message,
                            "url": url,
                            "domain": domain,
                            "website_info": website_info,
                            "method": "browser_automation",
                            "login_result": login_result
                        }
                        
                    except Exception as e:
                        # 如果自动化失败，回退到简单打开
                        webbrowser.open(url)
                        return {
                            "success": True,
                            "message": f"已打开网站: {url} (自动化失败，使用默认浏览器)",
                            "url": url,
                            "domain": domain,
                            "website_info": website_info,
                            "method": "browser_open",
                            "error": str(e)
                        }
                        
            except Exception as e:
                # 如果所有方法都失败，使用默认浏览器
                webbrowser.open(url)
                return {
                    "success": True,
                    "message": f"已打开网站: {url} (使用默认浏览器)",
                    "url": url,
                    "domain": domain,
                    "website_info": website_info,
                    "method": "browser_open",
                    "error": str(e)
                }
            
        except Exception as e:
            logger.error(f"打开网站失败: {e}")
            return {
                "success": False,
                "error": f"打开网站失败: {str(e)}"
            }
    
    def search_website(self, keyword: str, website: str = "") -> Dict[str, Any]:
        """在指定网站搜索"""
        try:
            if website:
                # 在指定网站搜索
                domain = website.lower()
                if domain not in self.website_configs:
                    return {
                        "success": False,
                        "error": f"不支持的网站: {website}"
                    }
                
                config = self.website_configs[domain]
                search_url = config['search_url'].format(keyword=keyword)
                
                webbrowser.open(search_url)
                
                return {
                    "success": True,
                    "message": f"在{config['name']}搜索: {keyword}",
                    "search_url": search_url,
                    "website": config['name'],
                    "keyword": keyword,
                    "method": "website_search"
                }
            else:
                # 在百度搜索
                search_url = f"https://www.baidu.com/s?wd={keyword}"
                webbrowser.open(search_url)
                
                return {
                    "success": True,
                    "message": f"在百度搜索: {keyword}",
                    "search_url": search_url,
                    "website": "百度",
                    "keyword": keyword,
                    "method": "baidu_search"
                }
                
        except Exception as e:
            logger.error(f"网站搜索失败: {e}")
            return {
                "success": False,
                "error": f"网站搜索失败: {str(e)}"
            }
    
    def get_website_summary(self, url: str) -> Dict[str, Any]:
        """获取网站信息总结"""
        try:
            # 标准化URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            domain = urlparse(url).netloc.lower()
            website_info = self._get_website_info(domain)
            
            # 尝试获取页面内容
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # 简单的页面分析
                content = response.text
                title = self._extract_title(content)
                description = self._extract_description(content)
                keywords = self._extract_keywords(content)
                
                summary = {
                    "success": True,
                    "url": url,
                    "domain": domain,
                    "website_info": website_info,
                    "title": title,
                    "description": description,
                    "keywords": keywords,
                    "content_length": len(content),
                    "status_code": response.status_code,
                    "method": "web_scraping"
                }
                
            except requests.RequestException:
                # 如果无法获取页面内容，返回基本信息
                summary = {
                    "success": True,
                    "url": url,
                    "domain": domain,
                    "website_info": website_info,
                    "title": website_info.get('name', 'Unknown'),
                    "description": f"这是一个{website_info.get('category', '未知')}网站",
                    "keywords": [],
                    "content_length": 0,
                    "status_code": 0,
                    "method": "basic_info"
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取网站总结失败: {e}")
            return {
                "success": False,
                "error": f"获取网站总结失败: {str(e)}"
            }
    
    def _get_website_info(self, domain: str) -> Dict[str, Any]:
        """获取网站信息"""
        # 移除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 查找匹配的网站配置
        for config_domain, config in self.website_configs.items():
            if domain == config_domain or domain.endswith('.' + config_domain):
                return config
        
        # 返回默认信息
        return {
            "name": domain,
            "category": "未知",
            "homepage": f"https://{domain}",
            "special_handlers": []
        }
    
    def _extract_title(self, content: str) -> str:
        """提取页面标题"""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()
        return "无标题"
    
    def _extract_description(self, content: str) -> str:
        """提取页面描述"""
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()
        return "无描述"
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取页面关键词"""
        keywords_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if keywords_match:
            keywords_str = keywords_match.group(1).strip()
            return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        return []

# 京东专用处理
class JDIntegration(ECommerceIntegration):
    """京东网站专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="京东",
            base_url="https://www.jd.com",
            search_url="https://search.jd.com/Search",
            product_url_template="https://item.jd.com/{product_id}.html"
        )
    
    def _build_search_url(self, keyword: str, page: int) -> str:
        """构建京东搜索URL"""
        return f"{self.search_url}?keyword={keyword}&page={page}"

# 淘宝专用处理
class TaobaoIntegration(ECommerceIntegration):
    """淘宝网站专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="淘宝",
            base_url="https://www.taobao.com",
            search_url="https://s.taobao.com/search",
            product_url_template="https://item.taobao.com/item.htm?id={product_id}"
        )
    
    def _build_search_url(self, keyword: str, page: int) -> str:
        """构建淘宝搜索URL"""
        return f"{self.search_url}?q={keyword}&s={44 * (page - 1)}"

# 高德地图专用处理
class AmapIntegration(BaseIntegration):
    """高德地图专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="高德地图",
            base_url="https://www.amap.com",
            search_url="https://uri.amap.com/search"
        )
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """构建高德地图搜索URL"""
        return f"{self.search_url}?query={keyword}"
    
    def get_route(self, start: str, end: str, mode: str = "driving") -> Dict[str, Any]:
        """获取高德地图路线"""
        try:
            route_url = f"https://uri.amap.com/navigation?from={start}&to={end}&mode={mode}"
            webbrowser.open(route_url)
            
            return {
                "success": True,
                "message": f"获取高德地图路线: {start} -> {end}",
                "route_url": route_url,
                "start": start,
                "end": end,
                "mode": mode,
                "method": "amap_route"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取高德地图路线失败: {str(e)}"
            }

# 拼多多专用处理
class PinduoduoIntegration(ECommerceIntegration):
    """拼多多网站专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="拼多多",
            base_url="https://www.pinduoduo.com",
            search_url="https://mobile.yangkeduo.com/search_result.html",
            product_url_template="https://mobile.yangkeduo.com/goods.html?goods_id={product_id}"
        )
    
    def _build_search_url(self, keyword: str, page: int) -> str:
        """构建拼多多搜索URL"""
        return f"{self.search_url}?search_key={keyword}&page={page}"

# 抖音专用处理
class DouyinIntegration(VideoPlatformIntegration):
    """抖音网站专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="抖音",
            base_url="https://www.douyin.com",
            search_url="https://www.douyin.com/search",
            video_url_template="https://www.douyin.com/video/{video_id}"
        )
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """构建抖音搜索URL"""
        return f"{self.search_url}/{keyword}"

# 快手专用处理
class KuaishouIntegration(VideoPlatformIntegration):
    """快手网站专用处理类"""
    
    def __init__(self):
        super().__init__(
            name="快手",
            base_url="https://www.kuaishou.com",
            search_url="https://www.kuaishou.com/search/video",
            video_url_template="https://www.kuaishou.com/video/{video_id}"
        )
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """构建快手搜索URL"""
        return f"{self.search_url}?searchKey={keyword}"

# 全局实例
website_integration = WebsiteIntegration()
jd_integration = JDIntegration()
taobao_integration = TaobaoIntegration()
amap_integration = AmapIntegration()
pinduoduo_integration = PinduoduoIntegration()
douyin_integration = DouyinIntegration()
kuaishou_integration = KuaishouIntegration()
