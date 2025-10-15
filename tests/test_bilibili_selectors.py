#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试B站搜索结果页面的选择器
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bilibili_selectors():
    """测试B站搜索结果页面的选择器"""
    print("测试B站搜索结果页面选择器")
    print("=" * 50)
    
    try:
        from src.tools.browser import automate_page
        
        # 测试UP主搜索结果页面
        print("测试UP主搜索结果页面...")
        result = automate_page(
            url="https://search.bilibili.com/upuser?keyword=影视飓风",
            steps=[
                {
                    "action": "wait",
                    "params": {"time": 5}
                },
                {
                    "action": "debug_page"
                }
            ],
            timeout_ms=10000
        )
        
        print(f"页面加载结果: {result}")
        
        if result.get('success'):
            print("✓ 页面加载成功")
            print(f"页面标题: {result.get('title', '')}")
            print(f"当前URL: {result.get('current_url', '')}")
            
            # 尝试获取页面内容
            try:
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=False)
                    context = browser.new_context()
                    page = context.new_page()
                    
                    page.goto("https://search.bilibili.com/upuser?keyword=影视飓风")
                    page.wait_for_load_state('domcontentloaded')
                    
                    # 获取页面HTML结构
                    html_content = page.content()
                    
                    # 查找可能的UP主选择器
                    selectors_to_test = [
                        ".up-item",
                        ".user-item", 
                        ".bili-user-card",
                        ".user-card",
                        ".up-card",
                        ".user-info",
                        ".up-info",
                        "a[href*='/space/']",
                        ".result-item",
                        ".search-result-item"
                    ]
                    
                    print("\n测试选择器:")
                    for selector in selectors_to_test:
                        try:
                            elements = page.query_selector_all(selector)
                            if elements:
                                print(f"✓ {selector}: 找到 {len(elements)} 个元素")
                                # 获取第一个元素的文本内容
                                if len(elements) > 0:
                                    text = elements[0].text_content()
                                    print(f"  第一个元素文本: {text[:50]}...")
                            else:
                                print(f"✗ {selector}: 未找到元素")
                        except Exception as e:
                            print(f"✗ {selector}: 错误 - {e}")
                    
                    browser.close()
                    
            except Exception as e:
                print(f"获取页面结构失败: {e}")
        else:
            print(f"✗ 页面加载失败: {result.get('error', '')}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_bilibili_selectors()
