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
    print("调试测试：检查B站搜索功能")
    print("=" * 60)
    
    # 简化的调试步骤
    steps = [
        {"action": "sleep", "ms": 5000},
        
        # 关闭可能的弹窗
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 2000},
        
        # 尝试多种方式找到搜索框
        {"action": "click", "selector": ".nav-search-input", "optional": True},
        {"action": "sleep", "ms": 1000},
        {"action": "click", "selector": "input[type='search']", "optional": True},
        {"action": "sleep", "ms": 1000},
        {"action": "click", "selector": "input[placeholder*='搜索']", "optional": True},
        {"action": "sleep", "ms": 1000},
        {"action": "click", "selector": "#nav-searchform input", "optional": True},
        {"action": "sleep", "ms": 1000},
        
        # 如果上面的都失败，尝试快捷键
        {"action": "press_global", "key": "/"},
        {"action": "sleep", "ms": 2000},
        
        # 清空并输入搜索内容
        {"action": "press_global", "key": "Control+A"},
        {"action": "sleep", "ms": 500},
        {"action": "press_global", "key": "Backspace"},
        {"action": "sleep", "ms": 500},
        {"action": "keyboard_type", "text": "影视飓风", "delay": 100},
        {"action": "sleep", "ms": 2000},
        
        # 按回车搜索
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 10000},  # 等待搜索结果
        
        # 等待任何搜索结果出现
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
        
        {"action": "sleep", "ms": 5000},
        
        # 尝试点击任何包含"影视飓风"的元素
        {"action": "click", "selector": "text=影视飓风", "optional": True},
        {"action": "sleep", "ms": 5000},
    ]
    
    try:
        result = automate_page(
            "https://www.bilibili.com", 
            steps, 
            headless=False, 
            timeout_ms=60000,
            keep_open_ms=30000  # 保持页面开启30秒
        )
        
        print(f"执行结果: {result.get('success')}")
        print(f"当前URL: {result.get('current_url')}")
        
        # 显示详细日志
        logs = result.get('logs', [])
        if logs:
            print("\n" + "=" * 40)
            print("完整执行日志:")
            print("=" * 40)
            for i, log in enumerate(logs, 1):
                print(f"{i:2d}. {log}")
        
    except Exception as e:
        print(f"[ERROR] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


