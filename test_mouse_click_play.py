#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.browser import automate_page


def main():
    url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    steps = [
        {"action": "sleep", "ms": 3000},
        {"action": "wait", "selector": "[class*='player'], .bpx-player-container, .bilibili-player, video", "state": "visible", "timeout": 15000},
        {"action": "sleep", "ms": 1000},
        {"action": "video_click_play"},
        {"action": "sleep", "ms": 4000}
    ]
    result = automate_page(url, steps, headless=False)
    print("success:", result.get("success"))
    print("current_url:", result.get("current_url"))


if __name__ == "__main__":
    main()










