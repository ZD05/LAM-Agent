#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试浏览器是否可见
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_browser_visible():
    """测试浏览器是否可见"""
    print("测试浏览器可见性")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        from src.tools.browser_config_safe import get_safe_browser_args, get_safe_browser_context_config
        
        with sync_playwright() as p:
            print("1. 启动浏览器...")
            browser = p.chromium.launch(
                headless=False,  # 确保显示浏览器
                args=get_safe_browser_args()
            )
            context = browser.new_context(**get_safe_browser_context_config())
            page = context.new_page()
            
            try:
                print("2. 打开淘宝主页...")
                page.goto("https://www.taobao.com", timeout=30000)
                time.sleep(3)
                
                print("3. 检查页面标题...")
                title = page.title()
                print(f"页面标题: {title}")
                
                print("4. 检查当前URL...")
                current_url = page.url
                print(f"当前URL: {current_url}")
                
                print("5. 查找登录按钮...")
                login_selectors = [
                    'a:has-text("登录")',
                    'a:has-text("请登录")',
                    '.h-login',
                    '#J_SiteNavLogin'
                ]
                
                for selector in login_selectors:
                    try:
                        count = page.locator(selector).count()
                        if count > 0:
                            print(f"找到登录按钮: {selector}")
                            print("6. 点击登录按钮...")
                            page.click(selector)
                            time.sleep(5)
                            
                            print("7. 检查登录页面...")
                            new_url = page.url
                            print(f"登录页面URL: {new_url}")
                            
                            # 检查登录表单
                            username_selectors = ['#fm-login-id', 'input[name="fm-login-id"]']
                            password_selectors = ['#fm-login-password', 'input[name="fm-login-password"]']
                            
                            for sel in username_selectors:
                                count = page.locator(sel).count()
                                if count > 0:
                                    print(f"找到用户名输入框: {sel}")
                            
                            for sel in password_selectors:
                                count = page.locator(sel).count()
                                if count > 0:
                                    print(f"找到密码输入框: {sel}")
                            
                            break
                    except Exception as e:
                        print(f"检查 {selector} 失败: {e}")
                
                print("8. 保持浏览器打开30秒...")
                print("请查看浏览器窗口，应该能看到淘宝登录页面")
                time.sleep(30)
                
            except Exception as e:
                print(f"测试过程中出错: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_browser_visible()


