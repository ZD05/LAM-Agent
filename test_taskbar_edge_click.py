import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置控制台编码
os.system("chcp 65001 > NUL")
os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.tools.bilibili import click_edge_taskbar_and_play_video

def main():
    print("Taskbar Edge Click + Video Play Test")
    print("=" * 50)
    
    up_name = "影视飓风"
    wait_ms = 10000  # 10秒停顿
    keep_open_ms = 60000  # 保持60秒
    
    print(f"UP: {up_name}")
    print(f"Wait: {wait_ms}ms")
    print(f"Keep open: {keep_open_ms}ms")
    print("Method: Click taskbar Edge icon")
    print("=" * 50)
    
    print("WARNING: This will click the Edge icon in your taskbar!")
    print("Make sure Edge is pinned to your taskbar.")
    print("Starting in 3 seconds...")
    
    import time
    time.sleep(3)
    
    try:
        result = click_edge_taskbar_and_play_video(
            up_name=up_name,
            wait_ms=wait_ms,
            keep_open_ms=keep_open_ms
        )
        
        print(f"Success: {result.get('success')}")
        print(f"URL: {result.get('current_url')}")
        
        if result.get('success'):
            print("SUCCESS: Test completed successfully!")
            print("Video should be playing in Edge browser now.")
        else:
            print("FAILED: Test failed")
            print(f"Error: {result.get('error')}")
            
        print("\nLog info:")
        logs = result.get('logs', [])
        for i, log in enumerate(logs[-10:], 1):
            print(f"{i:2d}. {log}")
            
    except Exception as e:
        print(f"Test exception: {e}")

if __name__ == "__main__":
    main()



