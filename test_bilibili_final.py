import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置控制台编码
os.system("chcp 65001 > NUL")
os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.tools.bilibili import search_and_play_first_video_strict

def main():
    print("Bilibili Search and Play Test")
    print("=" * 40)
    
    up_name = "影视飓风"
    wait_ms = 10000  # 10秒停顿
    keep_open_ms = 60000  # 保持60秒
    
    print(f"UP: {up_name}")
    print(f"Wait: {wait_ms}ms")
    print(f"Keep open: {keep_open_ms}ms")
    print("=" * 40)
    
    result = search_and_play_first_video_strict(
        up_name=up_name,
        keep_open_ms=keep_open_ms
    )
    
    print(f"Success: {result.get('success')}")
    print(f"URL: {result.get('current_url')}")
    
    if result.get('success'):
        print("Test completed successfully!")
        print("Video should be playing now.")
    else:
        print("Test failed")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    main()
