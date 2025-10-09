#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 强制UTF-8输出
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from src.tools.browser import automate_page


def main():
    print("=" * 60)
    print("测试：简化搜索并点击影视飓风")
    print("=" * 60)
    
    up_name = "影视飓风"
    timeout_ms = 120000  # 120秒超时
    
    print(f"目标UP主: {up_name}")
    print(f"超时时间: {timeout_ms}ms")
    print("=" * 60)
    
    # 简化的步骤
    steps = [
        {"action": "sleep", "ms": 5000},
        
        # 关闭可能的弹窗
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 3000},
        
        # 尝试多种方式找到搜索框
        {"action": "click", "selector": ".nav-search-input", "optional": True},
        {"action": "sleep", "ms": 2000},
        {"action": "click", "selector": "input[type='search']", "optional": True},
        {"action": "sleep", "ms": 2000},
        {"action": "click", "selector": "input[placeholder*='搜索']", "optional": True},
        {"action": "sleep", "ms": 2000},
        {"action": "press_global", "key": "/"},
        {"action": "sleep", "ms": 3000},
        
        # 清空并输入搜索内容
        {"action": "press_global", "key": "Control+A"},
        {"action": "sleep", "ms": 1000},
        {"action": "press_global", "key": "Backspace"},
        {"action": "sleep", "ms": 1000},
        {"action": "keyboard_type", "text": up_name, "delay": 150},
        {"action": "sleep", "ms": 3000},
        
        # 按回车搜索
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 15000},  # 等待搜索结果
        
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
        ], "timeout": 60000},
        
        {"action": "sleep", "ms": 5000},
        
        # 尝试点击影视飓风相关的链接
        {"action": "click_any", "selectors": [
            # 基于您提供的HTML结构的选择器
            "a.bili-video-card__info--owner[href*='space.bilibili.com/946974']",
            "a.bili-video-card__info--owner:has-text('影视飓风')",
            "a:has(.bili-video-card__info--author:has-text('影视飓风'))",
            
            # 通用的space链接
            "a[href*='space.bilibili.com/946974']",
            "a[href*='//space.bilibili.com/946974']",
            "a[href*='/space/946974']",
            "a[href*='space.bilibili.com']:has-text('影视飓风')",
            "a[href*='/space/']:has-text('影视飓风')",
            
            # 任何包含影视飓风文本的链接
            "a:has-text('影视飓风')",
        ], "new_page": True, "optional": True},
        
        {"action": "sleep", "ms": 5000},
        
        # 如果上面的选择器都失败，尝试点击包含UP主名称的文本
        {"action": "click", "selector": f"text={up_name}", "optional": True},
        {"action": "sleep", "ms": 5000},
        
        # 验证是否成功进入主页
        {"action": "wait_url", "includes": "space.bilibili.com", "timeout": 15000, "optional": True},
        {"action": "sleep", "ms": 3000},
    ]
    
    try:
        result = automate_page(
            "https://www.bilibili.com", 
            steps, 
            headless=False, 
            timeout_ms=timeout_ms,
            keep_open_ms=60000  # 保持页面开启60秒
        )
        
        print(f"执行结果: {result.get('success')}")
        print(f"当前URL: {result.get('current_url')}")
        
        if result.get('success'):
            print("[SUCCESS] 测试成功！已成功进入影视飓风主页")
            print("页面将保持开启60秒，您可以手动查看")
        else:
            print("[FAILED] 测试失败")
            error = result.get('error', '未知错误')
            print(f"错误信息: {error}")
        
        # 显示日志
        logs = result.get('logs', [])
        if logs:
            print("\n" + "=" * 40)
            print("执行日志 (最后20条):")
            print("=" * 40)
            for log in logs[-20:]:
                print(log)
        
    except Exception as e:
        print(f"[ERROR] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


