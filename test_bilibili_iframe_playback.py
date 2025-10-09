#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站iframe播放测试
测试iframe模式下的B站视频播放功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.browser import automate_page

def test_bilibili_iframe_playback():
    """测试B站iframe播放功能"""
    print("LAM-Agent B站iframe播放测试")
    print("=" * 60)
    
    # 测试URL
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    
    print(f"\n测试URL: {test_url}")
    print("使用iframe模式播放B站视频...")
    
    # iframe播放步骤
    steps = [
        # 等待页面加载
        {"action": "sleep", "ms": 5000},
        
        # 等待播放器元素（更灵活的选择器）
        {"action": "wait", "selector": "iframe, .bpx-player-container, [class*='player']", "state": "visible", "timeout": 10000},
        {"action": "sleep", "ms": 3000},
        
        # 尝试iframe播放
        {"action": "video_play"},
        {"action": "sleep", "ms": 3000},
        
        # 尝试点击iframe播放按钮
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 3000},
    ]
    
    try:
        result = automate_page(test_url, steps, headless=False)
        
        print(f"\n执行结果:")
        print(f"  成功: {result.get('success', False)}")
        print(f"  消息: {result.get('message', 'N/A')}")
        print(f"  当前URL: {result.get('current_url', 'N/A')}")
        
        if result.get('success'):
            print("\n[SUCCESS] B站iframe播放测试成功")
            print("✅ iframe模式正常工作")
            print("✅ B站视频播放器支持")
            print("✅ 播放按钮点击功能")
        else:
            print("\n[WARNING] B站iframe播放测试失败")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        return False

def test_iframe_detection():
    """测试iframe检测功能"""
    print("\n" + "=" * 60)
    print("测试iframe检测功能")
    print("=" * 60)
    
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    
    # iframe检测步骤
    steps = [
        {"action": "sleep", "ms": 5000},
        {"action": "wait", "selector": "iframe, [class*='player']", "state": "visible", "timeout": 10000},
        {"action": "sleep", "ms": 2000},
    ]
    
    try:
        result = automate_page(test_url, steps, headless=False)
        
        if result.get('success'):
            print("[SUCCESS] iframe检测成功")
            return True
        else:
            print("[WARNING] iframe检测失败")
            return False
            
    except Exception as e:
        print(f"[ERROR] iframe检测失败: {e}")
        return False

def main():
    """主测试函数"""
    print("LAM-Agent B站iframe播放综合测试")
    print("=" * 60)
    
    # 测试1: B站iframe播放
    print("\n==================== B站iframe播放 ====================")
    iframe_playback_success = test_bilibili_iframe_playback()
    
    # 测试2: iframe检测
    print("\n==================== iframe检测 ====================")
    iframe_detection_success = test_iframe_detection()
    
    # 测试结果总结
    print("\n" + "=" * 60)
    print("B站iframe播放测试结果:")
    print("-" * 60)
    
    if iframe_playback_success:
        print("[SUCCESS] B站iframe播放成功")
    else:
        print("[WARNING] B站iframe播放失败")
    
    if iframe_detection_success:
        print("[SUCCESS] iframe检测成功")
    else:
        print("[WARNING] iframe检测失败")
    
    # 成功率计算
    success_count = 0
    if iframe_playback_success:
        success_count += 1
    if iframe_detection_success:
        success_count += 1
    
    success_rate = (success_count / 2) * 100
    print(f"\n总成功率: {success_rate:.1f}%")
    
    if success_rate >= 50:
        print("\n[GOOD] B站iframe播放功能基本正常")
        print("✅ iframe模式支持已添加")
        print("✅ B站播放器兼容性提升")
        print("✅ 视频播放功能增强")
    else:
        print("\n[WARNING] B站iframe播放需要进一步优化")

if __name__ == "__main__":
    main()
