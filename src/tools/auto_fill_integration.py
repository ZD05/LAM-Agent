#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database.credential_db import credential_db

logger = logging.getLogger(__name__)

class AutoFillIntegration:
    """自动填充集成类，提供网页和应用的自动填充功能"""
    
    def __init__(self):
        # 网站域名与应用名称映射
        self.domain_mapping = {
            'baidu.com': '百度',
            'google.com': 'Google',
            'bing.com': 'Bing',
            'taobao.com': '淘宝',
            'tmall.com': '天猫',
            'jd.com': '京东',
            'pinduoduo.com': '拼多多',
            'weibo.com': '微博',
            'zhihu.com': '知乎',
            'bilibili.com': '哔哩哔哩',
            'douyin.com': '抖音',
            'kuaishou.com': '快手',
            'github.com': 'GitHub',
            'gitee.com': 'Gitee',
            'steam.com': 'Steam',
            'epicgames.com': 'Epic Games',
            'qq.com': 'QQ',
            'wechat.com': '微信',
            '163.com': '网易邮箱',
            '126.com': '网易邮箱',
            'sina.com': '新浪邮箱',
            'outlook.com': 'Outlook',
            'gmail.com': 'Gmail',
            'amap.com': '高德地图',
            'ditu.baidu.com': '百度地图',
            'open.weixin.qq.com': '微信开放平台',
            'mp.weixin.qq.com': '微信公众号',
            'work.weixin.qq.com': '企业微信'
        }
        
        # 应用名称标准化映射
        self.app_name_mapping = {
            'wechat': '微信',
            'weixin': '微信',
            'qq': 'QQ',
            'wps': 'WPS Office',
            'wpsoffice': 'WPS Office',
            'office': 'Microsoft Office',
            'steam': 'Steam',
            'bilibili': '哔哩哔哩',
            'b站': '哔哩哔哩',
            'douyin': '抖音',
            'kuaishou': '快手',
            'taobao': '淘宝',
            'tmall': '天猫',
            'jd': '京东',
            'pinduoduo': '拼多多',
            'baidu': '百度',
            'google': 'Google',
            'github': 'GitHub',
            'gitee': 'Gitee'
        }
    
    def extract_application_from_url(self, url: str) -> Optional[str]:
        """从URL中提取应用名称"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # 移除www前缀
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # 查找域名映射
            for mapped_domain, app_name in self.domain_mapping.items():
                if mapped_domain in domain:
                    return app_name
            
            # 如果没有找到映射，返回域名作为应用名称
            return domain.split('.')[0].title()
            
        except Exception as e:
            logger.error(f"从URL提取应用名称失败: {e}")
            return None
    
    def normalize_application_name(self, app_name: str) -> str:
        """标准化应用名称"""
        app_name_lower = app_name.lower().strip()
        
        # 查找标准化映射
        for key, value in self.app_name_mapping.items():
            if key in app_name_lower:
                return value
        
        # 如果没有找到映射，返回原始名称
        return app_name.strip()
    
    def auto_fill_for_website(self, url: str, username_field: str = "", password_field: str = "") -> Dict[str, Any]:
        """为网站自动填充凭据"""
        try:
            # 提取应用名称
            app_name = self.extract_application_from_url(url)
            if not app_name:
                return {
                    "success": False,
                    "error": "无法从URL提取应用名称"
                }
            
            # 标准化应用名称
            normalized_app_name = self.normalize_application_name(app_name)
            
            # 获取凭据
            result = credential_db.auto_fill_credential(normalized_app_name, url)
            
            if result["success"]:
                cred = result["credential"]
                return {
                    "success": True,
                    "message": f"找到 {normalized_app_name} 的凭据",
                    "application": normalized_app_name,
                    "url": url,
                    "credential": {
                        "username": cred["username"],
                        "account": cred["account"],
                        "password": cred["password"],
                        "contact": cred["contact"],
                        "notes": cred["notes"]
                    },
                    "fill_instructions": {
                        "username_field": username_field or "用户名输入框",
                        "password_field": password_field or "密码输入框"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到 {normalized_app_name} 的凭据",
                    "application": normalized_app_name,
                    "url": url,
                    "suggestion": f"请先在凭据管理器中添加 {normalized_app_name} 的凭据"
                }
                
        except Exception as e:
            logger.error(f"网站自动填充失败: {e}")
            return {
                "success": False,
                "error": f"网站自动填充失败: {str(e)}"
            }
    
    def auto_fill_for_application(self, app_name: str, username_field: str = "", password_field: str = "") -> Dict[str, Any]:
        """为应用自动填充凭据"""
        try:
            # 标准化应用名称
            normalized_app_name = self.normalize_application_name(app_name)
            
            # 获取凭据
            result = credential_db.auto_fill_credential(normalized_app_name)
            
            if result["success"]:
                cred = result["credential"]
                return {
                    "success": True,
                    "message": f"找到 {normalized_app_name} 的凭据",
                    "application": normalized_app_name,
                    "credential": {
                        "username": cred["username"],
                        "account": cred["account"],
                        "password": cred["password"],
                        "contact": cred["contact"],
                        "notes": cred["notes"]
                    },
                    "fill_instructions": {
                        "username_field": username_field or "用户名输入框",
                        "password_field": password_field or "密码输入框"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到 {normalized_app_name} 的凭据",
                    "application": normalized_app_name,
                    "suggestion": f"请先在凭据管理器中添加 {normalized_app_name} 的凭据"
                }
                
        except Exception as e:
            logger.error(f"应用自动填充失败: {e}")
            return {
                "success": False,
                "error": f"应用自动填充失败: {str(e)}"
            }
    
    def smart_auto_fill(self, identifier: str, identifier_type: str = "auto") -> Dict[str, Any]:
        """智能自动填充"""
        try:
            if identifier_type == "url" or (identifier_type == "auto" and identifier.startswith(('http://', 'https://'))):
                return self.auto_fill_for_website(identifier)
            elif identifier_type == "app" or identifier_type == "auto":
                return self.auto_fill_for_application(identifier)
            else:
                return {
                    "success": False,
                    "error": f"不支持的标识符类型: {identifier_type}"
                }
                
        except Exception as e:
            logger.error(f"智能自动填充失败: {e}")
            return {
                "success": False,
                "error": f"智能自动填充失败: {str(e)}"
            }
    
    def get_suggested_credentials(self, application: str, limit: int = 5) -> Dict[str, Any]:
        """获取建议的凭据列表"""
        try:
            # 标准化应用名称
            normalized_app_name = self.normalize_application_name(application)
            
            # 搜索相关凭据
            result = credential_db.search_credentials(normalized_app_name)
            
            if result["success"]:
                credentials = result["credentials"][:limit]
                return {
                    "success": True,
                    "application": normalized_app_name,
                    "suggestions": [
                        {
                            "id": cred["id"],
                            "username": cred["username"],
                            "account": cred["account"],
                            "application": cred["application"],
                            "notes": cred["notes"]
                        }
                        for cred in credentials
                    ],
                    "count": len(credentials)
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"获取建议凭据失败: {e}")
            return {
                "success": False,
                "error": f"获取建议凭据失败: {str(e)}"
            }
    
    def validate_credential_format(self, username: str, password: str, application: str) -> Dict[str, Any]:
        """验证凭据格式"""
        try:
            validation_result = {
                "success": True,
                "warnings": [],
                "suggestions": []
            }
            
            # 验证用户名
            if not username or len(username.strip()) == 0:
                validation_result["warnings"].append("用户名为空")
            elif len(username) < 2:
                validation_result["warnings"].append("用户名过短")
            
            # 验证密码
            if not password or len(password.strip()) == 0:
                validation_result["warnings"].append("密码为空")
            elif len(password) < 6:
                validation_result["warnings"].append("密码过短，建议至少6位")
            
            # 验证应用名称
            if not application or len(application.strip()) == 0:
                validation_result["warnings"].append("应用名称为空")
            
            # 密码强度检查
            if password:
                strength_score = self._calculate_password_strength(password)
                if strength_score < 3:
                    validation_result["suggestions"].append("建议使用更复杂的密码")
                elif strength_score >= 4:
                    validation_result["suggestions"].append("密码强度良好")
            
            # 应用名称建议
            if application:
                normalized_app = self.normalize_application_name(application)
                if normalized_app != application:
                    validation_result["suggestions"].append(f"建议使用标准应用名称: {normalized_app}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"验证凭据格式失败: {e}")
            return {
                "success": False,
                "error": f"验证凭据格式失败: {str(e)}"
            }
    
    def _calculate_password_strength(self, password: str) -> int:
        """计算密码强度"""
        score = 0
        
        # 长度检查
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # 字符类型检查
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[0-9]', password):
            score += 1
        if re.search(r'[^a-zA-Z0-9]', password):
            score += 1
        
        return min(score, 5)
    
    def get_auto_fill_statistics(self) -> Dict[str, Any]:
        """获取自动填充统计信息"""
        try:
            # 获取所有凭据
            result = credential_db.get_all_credentials()
            
            if result["success"]:
                credentials = result["credentials"]
                
                # 统计信息
                stats = {
                    "total_credentials": len(credentials),
                    "applications": {},
                    "categories": {},
                    "recent_usage": []
                }
                
                # 按应用统计
                for cred in credentials:
                    app = cred["application"]
                    if app not in stats["applications"]:
                        stats["applications"][app] = 0
                    stats["applications"][app] += 1
                
                # 按分类统计
                categories_result = credential_db.get_application_categories()
                if categories_result["success"]:
                    for category in categories_result["categories"]:
                        category_name = category["category_name"]
                        count = category["credential_count"]
                        stats["categories"][category_name] = count
                
                return {
                    "success": True,
                    "statistics": stats
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"获取自动填充统计失败: {e}")
            return {
                "success": False,
                "error": f"获取自动填充统计失败: {str(e)}"
            }

# 全局实例
auto_fill_integration = AutoFillIntegration()


