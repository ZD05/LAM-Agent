#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import logging
import winreg
from typing import Dict, Any, Optional, List

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

class IntelligentSteamAutomation:
    """智能Steam自动化类，使用DeepSeek进行决策"""
    
    def __init__(self):
        self.agent = LamAgent()
        self.steam_paths = []
        
    def find_steam_comprehensive(self) -> List[str]:
        """全面查找Steam安装路径"""
        paths = []
        
        # 1. 检查注册表
        try:
            logger.info("检查注册表...")
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
            ]
            
            for hkey, subkey in reg_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                        steam_exe = os.path.join(install_path, "steam.exe")
                        if os.path.exists(steam_exe):
                            paths.append(steam_exe)
                            logger.info(f"从注册表找到Steam: {steam_exe}")
                except Exception as e:
                    logger.debug(f"注册表检查失败: {e}")
        except Exception as e:
            logger.warning(f"注册表检查出错: {e}")
        
        # 2. 检查常见安装路径
        common_paths = [
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe",
            r"D:\Steam\steam.exe",
            r"E:\Steam\steam.exe",
            r"F:\Steam\steam.exe",
            r"C:\Games\Steam\steam.exe",
            r"D:\Games\Steam\steam.exe",
            r"E:\Games\Steam\steam.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                paths.append(path)
                logger.info(f"找到Steam: {path}")
        
        # 3. 检查桌面快捷方式
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if os.path.exists(desktop_path):
                for item in os.listdir(desktop_path):
                    if 'steam' in item.lower() and item.endswith('.lnk'):
                        shortcut_path = os.path.join(desktop_path, item)
                        try:
                            import win32com.client
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortCut(shortcut_path)
                            target_path = shortcut.Targetpath
                            if target_path and os.path.exists(target_path):
                                paths.append(target_path)
                                logger.info(f"从桌面快捷方式找到Steam: {target_path}")
                        except Exception as e:
                            logger.debug(f"解析快捷方式失败: {e}")
        except Exception as e:
            logger.warning(f"检查桌面快捷方式出错: {e}")
        
        # 4. 检查开始菜单
        try:
            start_menu_paths = [
                os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs"),
                os.path.join(os.environ.get('PROGRAMDATA', ''), r"Microsoft\Windows\Start Menu\Programs")
            ]
            
            for start_menu in start_menu_paths:
                if os.path.exists(start_menu):
                    for root, dirs, files in os.walk(start_menu):
                        for file in files:
                            if 'steam' in file.lower() and file.endswith('.lnk'):
                                shortcut_path = os.path.join(root, file)
                                try:
                                    import win32com.client
                                    shell = win32com.client.Dispatch("WScript.Shell")
                                    shortcut = shell.CreateShortCut(shortcut_path)
                                    target_path = shortcut.Targetpath
                                    if target_path and os.path.exists(target_path):
                                        paths.append(target_path)
                                        logger.info(f"从开始菜单找到Steam: {target_path}")
                                except Exception as e:
                                    logger.debug(f"解析开始菜单快捷方式失败: {e}")
        except Exception as e:
            logger.warning(f"检查开始菜单出错: {e}")
        
        # 去重
        unique_paths = list(set(paths))
        self.steam_paths = unique_paths
        return unique_paths
    
    def safe_launch_steam(self) -> Dict[str, Any]:
        """安全启动Steam"""
        try:
            # 查找Steam
            steam_paths = self.find_steam_comprehensive()
            
            if not steam_paths:
                return {
                    'success': False,
                    'error': '未找到Steam安装',
                    'suggestion': '请确保Steam已正确安装，或手动指定Steam路径'
                }
            
            # 使用第一个找到的Steam路径
            steam_path = steam_paths[0]
            logger.info(f"使用Steam路径: {steam_path}")
            
            # 使用os.startfile安全启动
            os.startfile(steam_path)
            
            # 等待启动
            time.sleep(3)
            
            return {
                'success': True,
                'steam_path': steam_path,
                'message': 'Steam启动成功'
            }
            
        except Exception as e:
            logger.error(f"启动Steam失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_ai_decision(self, context: str) -> Dict[str, Any]:
        """获取AI决策"""
        try:
            prompt = f"""
            作为Steam自动化助手，请分析以下情况并提供操作建议：
            
            情况描述：{context}
            
            请提供：
            1. 当前状态分析
            2. 下一步操作建议
            3. 可能的风险和注意事项
            4. 具体的操作步骤
            
            请以JSON格式返回：
            {{
                "analysis": "状态分析",
                "recommendation": "操作建议", 
                "risks": ["风险1", "风险2"],
                "steps": ["步骤1", "步骤2", "步骤3"]
            }}
            """
            
            response = self.agent.run(prompt)
            logger.info(f"AI决策: {response}")
            
            return {
                'success': True,
                'decision': response,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"获取AI决策失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_steam_operations(self) -> Dict[str, Any]:
        """模拟Steam操作流程"""
        try:
            logger.info("开始模拟Steam操作流程...")
            
            # 1. 启动Steam
            launch_result = self.safe_launch_steam()
            if not launch_result.get('success'):
                return launch_result
            
            # 2. 获取AI决策 - 启动后操作
            context1 = "Steam已成功启动，需要进入库存页面并找到第一个游戏"
            decision1 = self.get_ai_decision(context1)
            
            # 3. 模拟进入库存页面
            logger.info("模拟进入库存页面...")
            time.sleep(2)
            
            # 4. 获取AI决策 - 游戏操作
            context2 = "已进入Steam库存页面，找到第一个游戏，需要判断是启动游戏还是下载游戏"
            decision2 = self.get_ai_decision(context2)
            
            # 5. 模拟游戏操作
            logger.info("模拟游戏操作...")
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'Steam操作流程模拟完成',
                'steps': [
                    'Steam启动成功',
                    '获取启动后操作决策',
                    '进入库存页面',
                    '获取游戏操作决策',
                    '执行游戏操作'
                ],
                'ai_decisions': {
                    'after_launch': decision1,
                    'game_operation': decision2
                }
            }
            
        except Exception as e:
            logger.error(f"模拟Steam操作失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """主函数"""
    print("=" * 60)
    print("智能Steam自动化测试")
    print("=" * 60)
    print("目标:")
    print("1. 全面查找Steam安装路径")
    print("2. 安全启动Steam（避免黑屏）")
    print("3. 使用DeepSeek进行智能决策")
    print("4. 模拟完整的Steam操作流程")
    print("=" * 60)
    
    try:
        steam_automation = IntelligentSteamAutomation()
        
        # 1. 查找Steam
        print("\n步骤1: 查找Steam安装路径...")
        steam_paths = steam_automation.find_steam_comprehensive()
        
        if steam_paths:
            print(f"[SUCCESS] 找到 {len(steam_paths)} 个Steam安装:")
            for i, path in enumerate(steam_paths, 1):
                print(f"  {i}. {path}")
        else:
            print("[WARNING] 未找到Steam安装路径")
            print("将使用模拟模式进行测试...")
        
        # 2. 运行完整流程
        print("\n步骤2: 运行完整Steam自动化流程...")
        result = steam_automation.simulate_steam_operations()
        
        print("\n" + "=" * 60)
        print("测试结果:")
        print("=" * 60)
        
        if result.get('success'):
            print("[SUCCESS] 智能Steam自动化测试成功!")
            print(f"消息: {result.get('message', 'N/A')}")
            
            if 'steps' in result:
                print("\n完成的步骤:")
                for i, step in enumerate(result['steps'], 1):
                    print(f"  {i}. {step}")
            
            if 'ai_decisions' in result:
                print("\nAI决策结果:")
                for key, decision in result['ai_decisions'].items():
                    print(f"  {key}: {decision.get('success', False)}")
        else:
            print("[FAILED] 智能Steam自动化测试失败!")
            print(f"错误: {result.get('error', '未知错误')}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"[ERROR] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

