#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from src.tools.bilibili import open_up_wait_and_play_first


def main():
    up = "影视飓风"
    # 停顿20秒(20000ms)后点击第一个视频播放，保持页面开启60秒
    result = open_up_wait_and_play_first(up_name=up, wait_ms=20000, keep_open_ms=60000)
    print("success:", result.get("success"))
    print("current_url:", result.get("current_url"))
    logs = result.get("logs") or []
    print("logs_tail:\n" + "\n".join(logs[-14:]))


if __name__ == "__main__":
    main()





