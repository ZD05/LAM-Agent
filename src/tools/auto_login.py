#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网站自动登录功能
检测网站登录需求，检索凭据库，执行自动登录操作
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

from ..database.credential_db import credential_db
from .browser_config_safe import get_safe_browser_args, get_safe_browser_context_config

logger = logging.getLogger(__name__)

class AutoLoginManager:
    """网站自动登录管理器"""
    
    def __init__(self):
        # 常见登录页面标识
        self.login_indicators = {
            # 页面标题关键词
            'title_keywords': [
                '登录', '登陆', 'login', 'sign in', 'signin',
                '用户登录', '会员登录', '账户登录', '账号登录'
            ],
            # URL路径关键词
            'url_keywords': [
                '/login', '/signin', '/sign-in', '/auth', '/account/login',
                '/user/login', '/member/login', '/passport/login'
            ],
            # 页面元素关键词
            'element_keywords': [
                'login', 'signin', 'sign-in', 'auth', 'password',
                'username', 'email', 'phone', 'account'
            ]
        }
        
        # 常见登录表单选择器
        self.login_selectors = {
            # 用户名/邮箱/手机号输入框
            'username_selectors': [
                'input[name="username"]',
                'input[name="email"]',
                'input[name="phone"]',
                'input[name="account"]',
                'input[name="user"]',
                'input[name="login"]',
                'input[type="email"]',
                'input[placeholder*="用户名"]',
                'input[placeholder*="邮箱"]',
                'input[placeholder*="手机"]',
                'input[placeholder*="账号"]',
                'input[placeholder*="login"]',
                'input[placeholder*="email"]',
                'input[placeholder*="phone"]',
                '#username', '#email', '#phone', '#account', '#user',
                '.username', '.email', '.phone', '.account', '.user'
            ],
            # 密码输入框
            'password_selectors': [
                'input[name="password"]',
                'input[name="pwd"]',
                'input[name="pass"]',
                'input[type="password"]',
                'input[placeholder*="密码"]',
                'input[placeholder*="password"]',
                '#password', '#pwd', '#pass',
                '.password', '.pwd', '.pass'
            ],
            # 登录按钮
            'login_button_selectors': [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("登录")',
                'button:has-text("登陆")',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'button:has-text("Sign in")',
                'a:has-text("登录")',
                'a:has-text("Login")',
                '.login-btn', '.login-button', '.signin-btn',
                '#login-btn', '#login-button', '#signin-btn'
            ],
            # 验证码相关
            'captcha_selectors': [
                'input[name="captcha"]',
                'input[name="code"]',
                'input[name="verify"]',
                'input[placeholder*="验证码"]',
                'input[placeholder*="captcha"]',
                'input[placeholder*="code"]',
                '#captcha', '#code', '#verify',
                '.captcha', '.code', '.verify'
            ]
        }
        
        # 网站特定的登录配置
        self.site_specific_configs = {
            'taobao.com': {
                'username_selector': '#fm-login-id',
                'password_selector': '#fm-login-password',
                'login_button_selector': '#login-form .fm-button',
                'terms_checkbox_selector': '#J_Agreement',
                'need_captcha': True
            },
            'tmall.com': {
                'username_selector': '#fm-login-id',
                'password_selector': '#fm-login-password',
                'login_button_selector': '#login-form .fm-button',
                'terms_checkbox_selector': '#J_Agreement',
                'need_captcha': True
            },
            'jd.com': {
                'username_selector': '#loginname',
                'password_selector': '#nloginpwd',
                'login_button_selector': '#loginsubmit',
                'terms_checkbox_selector': '#agree',
                'need_captcha': True
            },
            'bilibili.com': {
                'username_selector': 'input[placeholder="请输入手机号/邮箱"]',
                'password_selector': 'input[placeholder="请输入密码"]',
                'login_button_selector': '.btn_primary',
                'terms_checkbox_selector': '.agree-checkbox',
                'need_captcha': True
            },
            'weibo.com': {
                'username_selector': 'input[name="username"]',
                'password_selector': 'input[name="password"]',
                'login_button_selector': 'a[action-type="btn_submit"]',
                'terms_checkbox_selector': 'input[name="agree"]',
                'need_captcha': False
            },
            'zhihu.com': {
                'username_selector': 'input[name="username"]',
                'password_selector': 'input[name="password"]',
                'login_button_selector': 'button[type="submit"]',
                'terms_checkbox_selector': 'input[name="agree"]',
                'need_captcha': True
            }
        }
    
    def detect_login_required(self, page) -> bool:
        """检测页面是否需要登录"""
        try:
            # 检查页面标题
            title = page.title().lower()
            for keyword in self.login_indicators['title_keywords']:
                if keyword.lower() in title:
                    logger.info(f"通过标题检测到登录页面: {title}")
                    return True
            
            # 检查URL
            url = page.url.lower()
            for keyword in self.login_indicators['url_keywords']:
                if keyword in url:
                    logger.info(f"通过URL检测到登录页面: {url}")
                    return True
            
            # 检查页面内容
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 检查是否有登录表单
            login_forms = soup.find_all('form')
            for form in login_forms:
                form_text = form.get_text().lower()
                if any(keyword in form_text for keyword in self.login_indicators['element_keywords']):
                    # 检查表单是否包含用户名和密码字段
                    username_inputs = form.find_all('input', {'name': re.compile(r'(username|email|phone|account|user|login)', re.I)})
                    password_inputs = form.find_all('input', {'type': 'password'})
                    
                    if username_inputs and password_inputs:
                        logger.info("通过表单检测到登录页面")
                        return True
            
            # 检查是否有登录按钮
            for selector in self.login_selectors['login_button_selectors']:
                try:
                    if page.locator(selector).count() > 0:
                        logger.info(f"通过登录按钮检测到登录页面: {selector}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"检测登录页面时出错: {e}")
            return False
    
    def get_credentials_for_site(self, url: str) -> Optional[Dict[str, str]]:
        """从凭据库获取网站对应的账号信息"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # 获取所有凭据
            cred_result = credential_db.get_all_credentials()
            
            if not cred_result.get('success'):
                logger.warning(f"获取凭据失败: {cred_result.get('error', '')}")
                return None
            
            credentials = cred_result.get('credentials', [])
            
            # 查找匹配的凭据
            for cred in credentials:
                # 处理不同的数据格式
                if isinstance(cred, dict):
                    is_active = cred.get('is_active', True)
                    website_url = cred.get('website_url', '')
                    application = cred.get('application', '')
                    account = cred.get('account', '')
                    password = cred.get('password', '')
                else:
                    # 如果是其他格式，跳过
                    continue
                
                if not is_active:
                    continue
                
                # 检查网站URL匹配
                if website_url and domain in website_url.lower():
                    logger.info(f"找到匹配的凭据: {application}")
                    return {
                        'username': account,
                        'password': self._decrypt_password(password),
                        'application': application
                    }
                
                # 检查应用名称匹配
                if application and self._is_site_match(domain, application.lower()):
                    logger.info(f"通过应用名称找到匹配的凭据: {application}")
                    return {
                        'username': account,
                        'password': self._decrypt_password(password),
                        'application': application
                    }
            
            logger.warning(f"未找到 {domain} 的凭据信息")
            return None
            
        except Exception as e:
            logger.error(f"获取凭据时出错: {e}")
            return None
    
    def _is_site_match(self, domain: str, application: str) -> bool:
        """检查域名和应用名称是否匹配"""
        domain_mapping = {
            'taobao.com': ['淘宝', 'taobao'],
            'tmall.com': ['天猫', 'tmall'],
            'jd.com': ['京东', 'jd', 'jingdong'],
            'bilibili.com': ['哔哩哔哩', 'bilibili', 'b站'],
            'weibo.com': ['微博', 'weibo'],
            'zhihu.com': ['知乎', 'zhihu'],
            'douyin.com': ['抖音', 'douyin'],
            'kuaishou.com': ['快手', 'kuaishou'],
            'pinduoduo.com': ['拼多多', 'pinduoduo'],
            'amap.com': ['高德地图', 'amap'],
            'github.com': ['github'],
            'gitee.com': ['gitee'],
            'steam.com': ['steam'],
            'qq.com': ['qq', '腾讯'],
            'wechat.com': ['微信', 'wechat']
        }
        
        if domain in domain_mapping:
            return any(keyword in application for keyword in domain_mapping[domain])
        
        return False
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """解密密码"""
        try:
            # 这里应该实现实际的解密逻辑
            # 目前返回原始密码（假设已经是明文）
            return encrypted_password
        except Exception as e:
            logger.error(f"解密密码时出错: {e}")
            return encrypted_password
    
    def find_login_elements(self, page, domain: str) -> Dict[str, Optional[str]]:
        """查找登录表单元素"""
        elements = {
            'username_selector': None,
            'password_selector': None,
            'login_button_selector': None,
            'captcha_selector': None
        }
        
        # 检查是否有网站特定配置
        if domain in self.site_specific_configs:
            config = self.site_specific_configs[domain]
            elements.update({
                'username_selector': config.get('username_selector'),
                'password_selector': config.get('password_selector'),
                'login_button_selector': config.get('login_button_selector'),
                'need_captcha': config.get('need_captcha', False)
            })
            return elements
        
        # 通用选择器查找
        try:
            # 查找用户名输入框
            for selector in self.login_selectors['username_selectors']:
                try:
                    if page.locator(selector).count() > 0:
                        elements['username_selector'] = selector
                        break
                except:
                    continue
            
            # 查找密码输入框
            for selector in self.login_selectors['password_selectors']:
                try:
                    if page.locator(selector).count() > 0:
                        elements['password_selector'] = selector
                        break
                except:
                    continue
            
            # 查找登录按钮
            for selector in self.login_selectors['login_button_selectors']:
                try:
                    if page.locator(selector).count() > 0:
                        elements['login_button_selector'] = selector
                        break
                except:
                    continue
            
            # 查找验证码输入框
            for selector in self.login_selectors['captcha_selectors']:
                try:
                    if page.locator(selector).count() > 0:
                        elements['captcha_selector'] = selector
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"查找登录元素时出错: {e}")
        
        return elements
    
    def perform_login(self, page, credentials: Dict[str, str], elements: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """执行登录操作"""
        try:
            username = credentials['username']
            password = credentials['password']
            
            # 等待页面加载完成
            page.wait_for_load_state('networkidle')
            
            # 填写用户名
            if elements['username_selector']:
                try:
                    page.fill(elements['username_selector'], username)
                    logger.info("已填写用户名")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"填写用户名失败: {e}")
                    return {
                        'success': False,
                        'error': f'填写用户名失败: {str(e)}'
                    }
            
            # 填写密码
            if elements['password_selector']:
                try:
                    page.fill(elements['password_selector'], password)
                    logger.info("已填写密码")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"填写密码失败: {e}")
                    return {
                        'success': False,
                        'error': f'填写密码失败: {str(e)}'
                    }
            
            # 勾选用户条款
            if elements.get('terms_checkbox_selector'):
                try:
                    # 检查条款复选框是否已勾选
                    is_checked = page.locator(elements['terms_checkbox_selector']).is_checked()
                    if not is_checked:
                        page.click(elements['terms_checkbox_selector'])
                        logger.info("已勾选用户条款")
                        time.sleep(1)
                    else:
                        logger.info("用户条款已勾选")
                except Exception as e:
                    logger.warning(f"勾选用户条款失败: {e}")
                    # 不因条款勾选失败而中断登录流程
            
            # 检查是否需要验证码
            captcha_selectors = [
                'input[placeholder*="验证码"]',
                'input[name="captcha"]',
                'input[name="code"]',
                'input[name="verify"]'
            ]
            
            captcha_found = False
            for selector in captcha_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        captcha_found = True
                        logger.warning(f"检测到验证码输入框: {selector}")
                        break
                except:
                    continue
            
            if captcha_found:
                logger.warning("检测到验证码，需要手动输入")
                return {
                    'success': False,
                    'error': '需要手动输入验证码',
                    'need_captcha': True,
                    'captcha_selector': selector
                }
            
            # 点击登录按钮
            if elements['login_button_selector']:
                try:
                    page.click(elements['login_button_selector'])
                    logger.info("已点击登录按钮")
                    
                    # 等待登录结果
                    time.sleep(3)
                    
                    # 检查登录是否成功
                    current_url = page.url
                    if self._is_login_successful(page, current_url):
                        logger.info("登录成功")
                        return {
                            'success': True,
                            'message': '登录成功',
                            'redirect_url': current_url
                        }
                    else:
                        logger.warning("登录可能失败，请检查凭据")
                        return {
                            'success': False,
                            'error': '登录失败，请检查用户名和密码',
                            'current_url': current_url
                        }
                        
                except Exception as e:
                    logger.error(f"点击登录按钮失败: {e}")
                    return {
                        'success': False,
                        'error': f'点击登录按钮失败: {str(e)}'
                    }
            else:
                logger.error("未找到登录按钮")
                return {
                    'success': False,
                    'error': '未找到登录按钮'
                }
                
        except Exception as e:
            logger.error(f"执行登录时出错: {e}")
            return {
                'success': False,
                'error': f'登录过程出错: {str(e)}'
            }
    
    def _is_login_successful(self, page, current_url: str) -> bool:
        """检查登录是否成功"""
        try:
            # 检查URL变化（通常登录成功会跳转）
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                return True
            
            # 检查页面内容变化
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 检查是否有用户信息显示
            user_indicators = [
                '用户中心', '个人中心', '我的账户', '我的主页',
                'logout', '退出', '个人资料', 'profile'
            ]
            
            page_text = soup.get_text().lower()
            for indicator in user_indicators:
                if indicator.lower() in page_text:
                    return True
            
            # 检查是否有错误信息
            error_indicators = [
                '用户名或密码错误', '登录失败', '账号不存在',
                'password error', 'login failed', 'invalid'
            ]
            
            for error in error_indicators:
                if error.lower() in page_text:
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态时出错: {e}")
            return False
    
    def auto_login_website(self, page, url: str) -> Dict[str, Any]:
        """网站自动登录主函数"""
        try:
            domain = urlparse(url).netloc.lower()
            logger.info(f"开始为网站 {domain} 执行自动登录")
            
            # 1. 检测是否需要登录
            if not self.detect_login_required(page):
                logger.info("页面不需要登录")
                return {
                    'success': True,
                    'message': '页面不需要登录',
                    'action': 'no_login_required'
                }
            
            # 2. 获取凭据
            credentials = self.get_credentials_for_site(url)
            if not credentials:
                logger.warning("未找到对应的凭据信息")
                return {
                    'success': False,
                    'error': '未找到对应的凭据信息，请先在凭据管理中添加账号',
                    'action': 'no_credentials'
                }
            
            # 3. 查找登录元素
            elements = self.find_login_elements(page, domain)
            if not elements['username_selector'] or not elements['password_selector']:
                logger.error("未找到登录表单元素")
                return {
                    'success': False,
                    'error': '未找到登录表单，可能页面结构已变化',
                    'action': 'elements_not_found'
                }
            
            # 4. 执行登录
            result = self.perform_login(page, credentials, elements)
            result['domain'] = domain
            result['action'] = 'login_attempted'
            
            return result
            
        except Exception as e:
            logger.error(f"自动登录过程中出错: {e}")
            return {
                'success': False,
                'error': f'自动登录失败: {str(e)}',
                'action': 'error'
            }

# 全局实例
auto_login_manager = AutoLoginManager()
