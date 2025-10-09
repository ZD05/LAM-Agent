#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.browser import automate_page


def main():
    # 从搜索引擎开始（Bing）
    url = "https://www.bing.com/"

    steps = [
        {"action": "sleep", "ms": 1200},
        # 搜索（允许这里用键盘输入，但从进入 B 站开始仅鼠标）
        {"action": "click", "selector": "input[name='q'], #sb_form_q"},
        {"action": "type", "selector": "input[name='q'], #sb_form_q", "text": "site:bilibili.com Python 教程", "clear": True},
        {"action": "press", "selector": "input[name='q'], #sb_form_q", "key": "Enter"},
        {"action": "sleep", "ms": 1800},
        # 点击第一个指向 B 站的自然结果（鼠标）
        {"action": "wait", "selector": "#b_results a[href*='bilibili.com']", "state": "visible", "timeout": 12000},
        {"action": "click", "selector": "#b_results a[href*='bilibili.com']"},
        {"action": "sleep", "ms": 2500},
        # 进入 B 站后，仅鼠标操作：点击第一个视频卡片/链接
        {"action": "wait", "selector": "a[href*='/video/'], .video-card a, .video-item a, .bili-video-card a", "state": "visible", "timeout": 15000},
        {"action": "click", "selector": "a[href*='/video/'], .bili-video-card a, .video-card a, .video-item a"},
        {"action": "sleep", "ms": 3000},
        # 等待播放器区域可见
        {"action": "wait", "selector": ".bpx-player-container, [class*='player'], .bilibili-player", "state": "visible", "timeout": 15000},
        {"action": "sleep", "ms": 800},
        # 仅鼠标方式触发播放
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 4000}
    ]

    result = automate_page(url, steps, headless=False)
    print("success:", result.get("success"))
    print("current_url:", result.get("current_url"))


if __name__ == "__main__":
    main()
