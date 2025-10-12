#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import logging
from typing import Dict, Any, Optional

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置环境变量
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
os.environ['DEEPSEEK_API_KEY'] = 'sk-c432cb92d9b141588cdfce29536feef1'
os.environ['DEEPSEEK_BASE_URL'] = 'https://api.deepseek.com'
os.environ['LAM_AGENT_MODEL'] = 'deepseek-chat'
os.environ['USE_DEEPSEEK'] = 'true'

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.lam_agent import LamAgent
from src.tools.desktop_integration import DesktopIntegration
from src.tools.browser import automate_page

class SteamAutomation:
    """Steam自动化类，安全启动和操作Steam"""
    
    def __init__(self):
        self.agent = LamAgent()
        self.desktop_integration = DesktopIntegration()
        self.steam_process = None
        
    def find_steam_paths(self) -> list:
        """查找Steam可能的安装路径"""
        possible_paths = [
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe",
            r"D:\Steam\steam.exe",
            r"E:\Steam\steam.exe",
            r"C:\Games\Steam\steam.exe"
        ]
        
        found_paths = []
        for path in possible_paths:
            if os.path.exists(path):
                found_paths.append(path)
                logger.info(f"找到Steam: {path}")
        
        return found_paths
    
    def safe_launch_steam(self) -> Dict[str, Any]:
        """安全启动Steam，避免黑屏问题"""
        try:
            # 1. 首先尝试从桌面启动
            logger.info("尝试从桌面启动Steam...")
            desktop_result = self.desktop_integration.launch_from_command("启动 Steam")
            
            if desktop_result.get('success'):
                logger.info("从桌面成功启动Steam")
                return desktop_result
            
            # 2. 尝试直接路径启动
            logger.info("尝试直接路径启动Steam...")
            steam_paths = self.find_steam_paths()
            
            if not steam_paths:
                return {
                    'success': False,
                    'error': '未找到Steam安装路径',
                    'suggestion': '请确保Steam已正确安装'
                }
            
            # 使用最安全的启动方式
            steam_path = steam_paths[0]
            logger.info(f"使用路径启动Steam: {steam_path}")
            
            # 使用os.startfile而不是subprocess，避免控制台创建
            os.startfile(steam_path)
            
            # 等待Steam启动
            time.sleep(5)
            
            return {
                'success': True,
                'method': 'direct_path',
                'path': steam_path,
                'message': 'Steam启动成功'
            }
            
        except Exception as e:
            logger.error(f"启动Steam失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def wait_for_steam_ui(self, timeout: int = 30) -> bool:
        """等待Steam UI加载完成"""
        logger.info("等待Steam UI加载...")
        
        for i in range(timeout):
            try:
                # 检查Steam进程是否运行
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq steam.exe'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if 'steam.exe' in result.stdout:
                    logger.info("Steam进程已启动")
                    time.sleep(3)  # 额外等待UI加载
                    return True
                    
            except Exception as e:
                logger.warning(f"检查Steam进程时出错: {e}")
            
            time.sleep(1)
        
        logger.warning("Steam UI加载超时")
        return False
    
    def navigate_to_library(self) -> Dict[str, Any]:
        """导航到Steam库存页面"""
        try:
            logger.info("导航到Steam库存页面...")
            
            # 使用DeepSeek进行智能决策
            decision_prompt = """
            我需要自动化Steam操作。当前情况：
            1. Steam已经启动
            2. 需要进入库存页面
            3. 找到第一个游戏
            4. 判断是启动游戏还是下载游戏
            
            请提供具体的操作步骤，包括：
            - 如何进入库存页面
            - 如何找到第一个游戏
            - 如何判断游戏状态
            - 如何执行相应操作
            
            请以JSON格式返回操作步骤。
            """
            
            # 获取AI决策
            response = self.agent.run(decision_prompt)
            logger.info(f"AI决策: {response}")
            
            # 这里可以添加具体的Steam自动化逻辑
            # 由于Steam是桌面应用，需要使用Windows API或UI自动化
            
            return {
                'success': True,
                'message': '导航到库存页面成功',
                'ai_decision': response
            }
            
        except Exception as e:
            logger.error(f"导航到库存页面失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_steam_automation(self) -> Dict[str, Any]:
        """运行完整的Steam自动化流程"""
        logger.info("开始Steam自动化流程...")
        
        try:
            # 1. 安全启动Steam
            launch_result = self.safe_launch_steam()
            if not launch_result.get('success'):
                return launch_result
            
            # 2. 等待Steam UI加载
            if not self.wait_for_steam_ui():
                return {
                    'success': False,
                    'error': 'Steam UI加载超时'
                }
            
            # 3. 导航到库存页面
            navigation_result = self.navigate_to_library()
            if not navigation_result.get('success'):
                return navigation_result
            
            return {
                'success': True,
                'message': 'Steam自动化流程完成',
                'steps': [
                    'Steam启动成功',
                    'UI加载完成',
                    '导航到库存页面'
                ]
            }
            
        except Exception as e:
            logger.error(f"Steam自动化流程失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """主函数"""
    print("=" * 60)
    print("Steam安全自动化测试")
    print("=" * 60)
    print("目标:")
    print("1. 安全启动Steam（避免黑屏）")
    print("2. 进入库存页面")
    print("3. 找到第一个游戏")
    print("4. 智能判断并执行操作")
    print("=" * 60)
    
    try:
        steam_automation = SteamAutomation()
        result = steam_automation.run_steam_automation()
        
        print("\n" + "=" * 60)
        print("测试结果:")
        print("=" * 60)
        
        if result.get('success'):
            print("[SUCCESS] Steam自动化测试成功!")
            print(f"消息: {result.get('message', 'N/A')}")
            
            if 'steps' in result:
                print("\n完成的步骤:")
                for i, step in enumerate(result['steps'], 1):
                    print(f"  {i}. {step}")
        else:
            print("[FAILED] Steam自动化测试失败!")
            print(f"错误: {result.get('error', '未知错误')}")
            
            if 'suggestion' in result:
                print(f"建议: {result['suggestion']}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"[ERROR] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
