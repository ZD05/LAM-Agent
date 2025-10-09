#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.executor import executor

def test_search_debug():
    """测试搜索调试"""
    print("B站搜索调试测试")
    print("=" * 50)
    
    up_name = "影视飓风"
    print(f"搜索UP主: {up_name}")
    
    try:
        # 执行搜索动作
        result = executor.execute_action('bilibili_search_play', {
            'keyword': up_name,
            'wait_ms': 5000,
            'keep_open_ms': 30000
        })
        
        print(f"执行结果: {result}")
        
    except Exception as e:
        print(f"执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_debug()



