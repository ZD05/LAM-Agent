#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 强制UTF-8输出
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from src.tools.browser import automate_page


def main():
    url = "https://www.bilibili.com"

    search_input_selectors = [
        "input#nav-searchform input",
        ".nav-search-input input",
        "input[type=search]",
        "input[placeholder*='搜索']",
        "input[placeholder*='搜']",
    ]
    search_click_helpers = [
        ".nav-search-input",
        ".nav-search-btn",
        ".nav-search-logo",
        "button:has-text('搜索')",
    ]
    result_card_selectors = [
        "a[href*='/video/']",
        ".bili-video-card a",
        ".video-item a",
        ".video-card a",
    ]

    steps = [
        {"action": "sleep", "ms": 2500},
        {"action": "click", "selector": "text=关闭, button:has-text('关闭'), .close-btn, .bili-guide, .mask, .btn-close, .cookie, .consent", "optional": True},
        {"action": "sleep", "ms": 600},
        {"action": "press_global", "key": "/"},
        {"action": "sleep", "ms": 300},
        {"action": "click", "selector": ", ".join(search_click_helpers), "optional": True},
        {"action": "sleep", "ms": 200},
        {"action": "click", "selector": ", ".join(search_input_selectors), "optional": True},
        {"action": "sleep", "ms": 300},
        {"action": "keyboard_type", "text": "影视飓风", "delay": 20},
        {"action": "sleep", "ms": 400},
        {"action": "press_global", "key": "Enter"},
        {"action": "sleep", "ms": 3000},
        {"action": "wait_any", "selectors": result_card_selectors, "timeout": 20000},
        {"action": "sleep", "ms": 900},
        {"action": "click_any", "selectors": result_card_selectors, "new_page": True},
        {"action": "wait_url", "includes": "/video/", "timeout": 20000},
        {"action": "sleep", "ms": 3000},
        {"action": "wait_video_ready", "timeout": 20000},
        {"action": "sleep", "ms": 1500},
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 2500},
        {"action": "video_play"},
        {"action": "sleep", "ms": 1500},
    ]

    result = automate_page(url, steps, headless=False, timeout_ms=45000)
    print("success:", result.get("success"))
    print("current_url:", result.get("current_url"))
    logs = result.get("logs") or []
    tail = logs[-10:]
    try:
        print("logs_tail:\n" + "\n".join(tail))
    except Exception:
        for line in tail:
            try:
                print(line.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
            except Exception:
                pass


if __name__ == "__main__":
    main()



