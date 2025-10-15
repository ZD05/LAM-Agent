#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAM-Agent 主启动脚本
统一入口，支持多种启动模式
"""

import sys
import argparse
import logging
from typing import Optional

# 环境变量与配置改由 src.config.Settings 统一管理（支持 .env 和系统环境变量）

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies() -> bool:
    """检查依赖"""
    try:
        import src.ui.chatgpt_ui
        import src.database.credential_db
        import src.agent.lam_agent
        return True
    except ImportError as e:
        print(f"依赖错误: {e}")
        print("请确保所有模块都已正确安装")
        return False

def start_gui():
    """启动图形界面"""
    try:
        from src.ui.chatgpt_ui import main as ui_main
        print("正在启动LAM-Agent ChatGPT风格UI...")
        ui_main()
    except Exception as e:
        print(f"启动UI失败: {e}")
        import traceback
        traceback.print_exc()

def start_cli(query: str, model: Optional[str] = None):
    """启动命令行界面"""
    try:
        from src.agent.lam_agent import LamAgent
        
        logger.info("初始化 LAM Agent...")
        agent = LamAgent(model=model)
        
        logger.info(f"处理查询: {query}")
        result = agent.run(query)
        
        print("\n" + "="*50)
        print("LAM Agent 回答:")
        print("="*50)
        print(result["answer"])
        
        if result.get("sources"):
            print("\n" + "-"*30)
            print("来源链接:")
            print("-"*30)
            for i, source in enumerate(result["sources"], 1):
                if source:
                    print(f"{i}. {source}")
        
        print(f"\n执行计划: {result['plan']}")
        print(f"证据数量: {result['evidence_count']}")
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"运行失败: {e}")
        print(f"错误: {e}")
        sys.exit(1)

def start_api():
    """启动API服务"""
    try:
        import uvicorn
        from src.api.main import app
        print("启动API服务...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"启动API服务失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LAM-Agent 智能桌面助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 启动图形界面
  python main.py --cli "你的问题"    # 命令行模式
  python main.py --api              # 启动API服务
  python main.py --help             # 显示帮助信息
        """
    )
    
    parser.add_argument(
        "--cli", 
        type=str, 
        help="命令行模式，直接回答问题"
    )
    parser.add_argument(
        "--api", 
        action="store_true", 
        help="启动API服务"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="指定使用的模型"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    try:
        if args.api:
            # 启动API服务
            start_api()
        elif args.cli:
            # 命令行模式
            start_cli(args.cli, args.model)
        else:
            # 默认启动图形界面
            start_gui()
            
    except Exception as e:
        logger.error(f"启动失败: {e}")
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
