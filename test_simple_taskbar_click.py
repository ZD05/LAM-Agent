import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置控制台编码
os.system("chcp 65001 > NUL")
os.environ['PYTHONIOENCODING'] = 'utf-8'

import pyautogui
import time

def main():
    print("Simple Taskbar Edge Click Test")
    print("=" * 40)
    
    # 设置pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    
    print("This will click the Edge icon in your taskbar!")
    print("Make sure Edge is pinned to your taskbar.")
    print("Starting in 3 seconds...")
    
    time.sleep(3)
    
    # 点击任务栏Edge图标
    edge_icon_x, edge_icon_y = 50, 1050
    print(f"Clicking Edge icon at ({edge_icon_x}, {edge_icon_y})")
    
    try:
        pyautogui.click(edge_icon_x, edge_icon_y)
        print("SUCCESS: Edge icon clicked!")
        print("Edge browser should be opening now.")
        
        # 等待一下让Edge打开
        time.sleep(3)
        print("Edge should be open now.")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    main()



