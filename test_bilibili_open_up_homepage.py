#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from src.tools.bilibili import open_up_homepage


def main():
    up = "影视飓风"
    result = open_up_homepage(up_name=up, keep_open_ms=60000)
    print("success:", result.get("success"))
    print("current_url:", result.get("current_url"))
    logs = result.get("logs") or []
    print("logs_tail:\n" + "\n".join(logs[-12:]))


if __name__ == "__main__":
    main()



