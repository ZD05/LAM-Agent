#!/usr/bin/env python3
"""
LAM-Agent 高级图形界面启动脚本
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查依赖"""
    try:
        import src.ui.advanced_window
        return True
    except ImportError as e:
        messagebox.showerror("依赖错误", f"缺少必要的依赖: {e}\n\n请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    # 设置环境变量
    os.environ['DEEPSEEK_API_KEY'] = 'sk-c432cb92d9b141588cdfce29536feef1'
    os.environ['DEEPSEEK_BASE_URL'] = 'https://api.deepseek.com'
    os.environ['LAM_AGENT_MODEL'] = 'deepseek-chat'
    os.environ['USE_DEEPSEEK'] = 'true'
    # 显式关闭无头模式，确保浏览器窗口可见
    os.environ['LAM_BROWSER_HEADLESS'] = 'false'
    
    # 检查依赖
    if not check_dependencies():
        return
    
    try:
        # 导入并启动高级UI
        from src.ui.advanced_window import main as ui_main
        ui_main()
    except Exception as e:
        messagebox.showerror("启动错误", f"无法启动应用程序: {e}")

if __name__ == "__main__":
    main()
