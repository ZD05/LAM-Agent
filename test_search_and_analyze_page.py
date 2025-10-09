#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 强制UTF-8输出
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from src.tools.browser import automate_page
import re


def analyze_page_for_yingshijufeng(page_content):
    """分析页面内容，寻找影视飓风相关的链接"""
    print("\n" + "=" * 50)
    print("页面内容分析")
    print("=" * 50)
    
    # 寻找包含"影视飓风"的链接
    yingshijufeng_links = []
    
    # 匹配各种可能的链接模式
    patterns = [
        r'<a[^>]*href=["\']([^"\']*space\.bilibili\.com[^"\']*)["\'][^>]*>.*?影视飓风.*?</a>',
        r'<a[^>]*>.*?影视飓风.*?</a>',
        r'href=["\']([^"\']*space\.bilibili\.com[^"\']*)["\'].*?影视飓风',
        r'影视飓风.*?href=["\']([^"\']*space\.bilibili\.com[^"\']*)["\']',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, page_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if match not in yingshijufeng_links:
                yingshijufeng_links.append(match)
    
    # 寻找包含"影视飓风"的文本和可能的链接
    lines = page_content.split('\n')
    for i, line in enumerate(lines):
        if '影视飓风' in line:
            print(f"找到包含'影视飓风'的行 {i+1}: {line[:200]}...")
            
            # 在这行中寻找链接
            link_matches = re.findall(r'href=["\']([^"\']*)["\']', line)
            for link in link_matches:
                if 'space.bilibili.com' in link or '/space/' in link:
                    if link not in yingshijufeng_links:
                        yingshijufeng_links.append(link)
                        print(f"  发现链接: {link}")
    
    print(f"\n找到的影视飓风相关链接数量: {len(yingshijufeng_links)}")
    for i, link in enumerate(yingshijufeng_links, 1):
        print(f"{i}. {link}")
    
    return yingshijufeng_links


def main():
    print("=" * 60)
    print("测试：搜索并分析页面代码寻找影视飓风主页链接")
    print("=" * 60)
    
    up_name = "影视飓风"
    timeout_ms = 90000  # 90秒超时
    
    print(f"目标UP主: {up_name}")
    print(f"超时时间: {timeout_ms}ms")
    print("=" * 60)
    
    # 步骤1：搜索
    search_steps = [
        {"action": "sleep", "ms": 3000},
        
        # 关闭可能的弹窗
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 2000},
        
        # 尝试找到搜索框
        {"action": "click", "selector": ".nav-search-input", "optional": True},
        {"action": "sleep", "ms": 1000},
        {"action": "press_global", "key": "/"},
        {"action": "sleep", "ms": 2000},
        
        # 清空并输入搜索内容
        {"action": "press_global", "key": "Control+A"},
        {"action": "sleep", "ms": 500},
        {"action": "press_global", "key": "Backspace"},
        {"action": "sleep", "ms": 500},
        {"action": "keyboard_type", "text": up_name, "delay": 100},
        {"action": "sleep", "ms": 2000},
        
        # 按回车搜索
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 10000},  # 等待搜索结果
        
        # 等待搜索结果出现
        {"action": "wait_any", "selectors": [
            ".bili-video-card",
            ".video-item",
            ".bili-video-item",
            ".video-card",
            ".video-list-item",
            ".up-item",
            ".user-item",
            ".result-item",
            ".bili-user-item",
            ".user-card",
            ".up-card",
            ".search-result",
            "a[href*='/video/']",
            "a[href*='/space/']",
            "*:has-text('影视飓风')",
        ], "timeout": 30000},
        
        {"action": "sleep", "ms": 3000},
    ]
    
    try:
        # 执行搜索步骤
        result = automate_page(
            "https://www.bilibili.com", 
            search_steps, 
            headless=False, 
            timeout_ms=timeout_ms,
            keep_open_ms=None  # 不自动关闭
        )
        
        print(f"搜索执行结果: {result.get('success')}")
        print(f"当前URL: {result.get('current_url')}")
        
        if not result.get('success'):
            print("[FAILED] 搜索步骤失败")
            return
        
        # 步骤2：获取页面内容并分析
        print("\n正在获取页面内容...")
        
        # 使用evaluate动作获取页面HTML内容
        get_content_steps = [
            {"action": "evaluate", "script": "document.documentElement.outerHTML"},
        ]
        
        content_result = automate_page(
            result.get('current_url', 'https://www.bilibili.com'), 
            get_content_steps, 
            headless=False, 
            timeout_ms=10000,
            keep_open_ms=None
        )
        
        # 从日志中提取页面内容
        page_content = ""
        if content_result.get('logs'):
            for log in content_result.get('logs', []):
                if 'document.documentElement.outerHTML' in str(log) and len(str(log)) > 1000:
                    page_content = str(log)
                    break
        
        if not page_content:
            print("[ERROR] 无法获取页面内容")
            return
        
        # 分析页面内容
        yingshijufeng_links = analyze_page_for_yingshijufeng(page_content)
        
        if not yingshijufeng_links:
            print("[WARNING] 未找到影视飓风相关的链接")
            return
        
        # 步骤3：尝试点击找到的链接
        print(f"\n尝试点击找到的链接...")
        
        # 选择最可能的链接（优先选择包含space.bilibili.com的）
        best_link = None
        for link in yingshijufeng_links:
            if 'space.bilibili.com' in link:
                best_link = link
                break
        
        if not best_link and yingshijufeng_links:
            best_link = yingshijufeng_links[0]
        
        if best_link:
            print(f"选择链接: {best_link}")
            
            # 构建点击步骤
            click_steps = [
                {"action": "sleep", "ms": 2000},
                # 尝试多种方式点击链接
                {"action": "click", "selector": f"a[href*='{best_link}']", "optional": True},
                {"action": "sleep", "ms": 2000},
                {"action": "click", "selector": f"a[href='{best_link}']", "optional": True},
                {"action": "sleep", "ms": 2000},
                {"action": "click", "selector": f"text=影视飓风", "optional": True},
                {"action": "sleep", "ms": 5000},
            ]
            
            # 执行点击步骤
            click_result = automate_page(
                result.get('current_url', 'https://www.bilibili.com'), 
                click_steps, 
                headless=False, 
                timeout_ms=30000,
                keep_open_ms=60000  # 保持页面开启60秒
            )
            
            print(f"点击执行结果: {click_result.get('success')}")
            print(f"最终URL: {click_result.get('current_url')}")
            
            if click_result.get('success'):
                print("[SUCCESS] 成功进入影视飓风主页！")
                print("页面将保持开启60秒，您可以手动查看")
            else:
                print("[FAILED] 点击链接失败")
        
        # 显示详细日志
        logs = result.get('logs', [])
        if logs:
            print("\n" + "=" * 40)
            print("搜索步骤日志 (最后10条):")
            print("=" * 40)
            for log in logs[-10:]:
                print(log)
        
    except Exception as e:
        print(f"[ERROR] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
