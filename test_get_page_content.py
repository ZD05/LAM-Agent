#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 强制UTF-8输出
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from src.tools.browser import automate_page
import re


def main():
    print("=" * 60)
    print("测试：获取页面内容并分析影视飓风链接")
    print("=" * 60)
    
    # 简化的步骤：搜索并获取页面内容
    steps = [
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
        {"action": "keyboard_type", "text": "影视飓风", "delay": 100},
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
        
        # 获取页面HTML内容
        {"action": "evaluate", "script": "document.documentElement.outerHTML"},
        
        {"action": "sleep", "ms": 2000},
    ]
    
    try:
        result = automate_page(
            "https://www.bilibili.com", 
            steps, 
            headless=False, 
            timeout_ms=90000,
            keep_open_ms=30000  # 保持页面开启30秒
        )
        
        print(f"执行结果: {result.get('success')}")
        print(f"当前URL: {result.get('current_url')}")
        
        # 从日志中提取页面内容
        page_content = ""
        logs = result.get('logs', [])
        
        print("\n" + "=" * 40)
        print("分析日志中的页面内容...")
        print("=" * 40)
        
        for i, log in enumerate(logs):
            if isinstance(log, str) and len(log) > 1000 and ('<html' in log or '<body' in log):
                page_content = log
                print(f"找到页面内容 (日志 {i+1}): {len(log)} 字符")
                break
        
        if not page_content:
            print("[WARNING] 未在日志中找到页面内容，尝试其他方法...")
            # 尝试从所有日志中拼接
            all_logs = " ".join([str(log) for log in logs if isinstance(log, str)])
            if len(all_logs) > 1000:
                page_content = all_logs
                print(f"使用所有日志拼接: {len(page_content)} 字符")
        
        if page_content:
            print(f"\n页面内容长度: {len(page_content)} 字符")
            
            # 分析页面内容
            print("\n" + "=" * 50)
            print("页面内容分析")
            print("=" * 50)
            
            # 寻找包含"影视飓风"的行
            lines = page_content.split('\n')
            yingshijufeng_lines = []
            
            for i, line in enumerate(lines):
                if '影视飓风' in line:
                    yingshijufeng_lines.append((i+1, line.strip()))
                    if len(yingshijufeng_lines) <= 10:  # 只显示前10行
                        print(f"行 {i+1}: {line.strip()[:200]}...")
            
            print(f"\n找到包含'影视飓风'的行数: {len(yingshijufeng_lines)}")
            
            # 寻找链接
            link_patterns = [
                r'href=["\']([^"\']*space\.bilibili\.com[^"\']*)["\']',
                r'href=["\']([^"\']*\/space\/[^"\']*)["\']',
            ]
            
            found_links = []
            for pattern in link_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    if match not in found_links:
                        found_links.append(match)
            
            print(f"\n找到的space链接数量: {len(found_links)}")
            for i, link in enumerate(found_links, 1):
                print(f"{i}. {link}")
            
            # 寻找包含"影视飓风"的链接
            yingshijufeng_links = []
            for line in yingshijufeng_lines:
                line_content = line[1]
                for pattern in link_patterns:
                    matches = re.findall(pattern, line_content, re.IGNORECASE)
                    for match in matches:
                        if match not in yingshijufeng_links:
                            yingshijufeng_links.append(match)
            
            print(f"\n找到的影视飓风相关链接数量: {len(yingshijufeng_links)}")
            for i, link in enumerate(yingshijufeng_links, 1):
                print(f"{i}. {link}")
            
            if yingshijufeng_links:
                # 尝试点击第一个链接
                best_link = yingshijufeng_links[0]
                print(f"\n尝试点击链接: {best_link}")
                
                click_steps = [
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": f"a[href*='{best_link}']", "optional": True},
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": f"a[href='{best_link}']", "optional": True},
                    {"action": "sleep", "ms": 2000},
                    {"action": "click", "selector": "text=影视飓风", "optional": True},
                    {"action": "sleep", "ms": 5000},
                ]
                
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
                else:
                    print("[FAILED] 点击链接失败")
        else:
            print("[ERROR] 无法获取页面内容")
        
        # 显示详细日志
        if logs:
            print("\n" + "=" * 40)
            print("执行日志 (最后10条):")
            print("=" * 40)
            for log in logs[-10:]:
                print(log)
        
    except Exception as e:
        print(f"[ERROR] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
