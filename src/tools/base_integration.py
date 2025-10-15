#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础集成类，提供通用的网站和软件集成功能
"""

import webbrowser
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseIntegration(ABC):
    """基础集成类"""
    
    def __init__(self, name: str, base_url: str, search_url: str):
        self.name = name
        self.base_url = base_url
        self.search_url = search_url
    
    def open_website(self, url: Optional[str] = None) -> Dict[str, Any]:
        """打开网站"""
        try:
            target_url = url or self.base_url
            webbrowser.open(target_url)
            
            return {
                "success": True,
                "message": f"打开{self.name}网站",
                "url": target_url,
                "method": f"{self.name.lower()}_open"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"打开{self.name}网站失败: {str(e)}"
            }
    
    def search(self, keyword: str, page: int = 1) -> Dict[str, Any]:
        """搜索功能"""
        try:
            search_url = self._build_search_url(keyword, page)
            webbrowser.open(search_url)
            
            return {
                "success": True,
                "message": f"在{self.name}搜索: {keyword}",
                "search_url": search_url,
                "keyword": keyword,
                "page": page,
                "method": f"{self.name.lower()}_search"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"{self.name}搜索失败: {str(e)}"
            }
    
    @abstractmethod
    def _build_search_url(self, keyword: str, page: int) -> str:
        """构建搜索URL"""
        pass

class ECommerceIntegration(BaseIntegration):
    """电商网站集成基类"""
    
    def __init__(self, name: str, base_url: str, search_url: str, product_url_template: str):
        super().__init__(name, base_url, search_url)
        self.product_url_template = product_url_template
    
    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """获取商品信息"""
        try:
            product_url = self.product_url_template.format(product_id=product_id)
            webbrowser.open(product_url)
            
            return {
                "success": True,
                "message": f"打开{self.name}商品页面: {product_id}",
                "product_url": product_url,
                "product_id": product_id,
                "method": f"{self.name.lower()}_product"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取{self.name}商品信息失败: {str(e)}"
            }

class VideoPlatformIntegration(BaseIntegration):
    """视频平台集成基类"""
    
    def __init__(self, name: str, base_url: str, search_url: str, video_url_template: str):
        super().__init__(name, base_url, search_url)
        self.video_url_template = video_url_template
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """获取视频信息"""
        try:
            video_url = self.video_url_template.format(video_id=video_id)
            webbrowser.open(video_url)
            
            return {
                "success": True,
                "message": f"打开{self.name}视频页面: {video_id}",
                "video_url": video_url,
                "video_id": video_id,
                "method": f"{self.name.lower()}_video"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取{self.name}视频信息失败: {str(e)}"
            }

