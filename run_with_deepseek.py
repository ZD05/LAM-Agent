#!/usr/bin/env python3
"""
使用DeepSeek运行LAM-Agent的启动脚本
"""
import sys
from src.config import validate_settings

try:
    validate_settings()
except Exception as e:
    print(f"配置错误: {e}\n\n请在项目根目录创建 .env 或设置环境变量。")
    sys.exit(1)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python run_with_deepseek.py '你的问题'")
        print("  python run_with_deepseek.py --api  # 启动API服务")
        return
    
    if sys.argv[1] == '--api':
        # 启动API服务
        print("启动API服务...")
        import uvicorn
        from src.api.main import app
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    else:
        # 运行CLI
        question = " ".join(sys.argv[1:])
        print(f"问题: {question}")
        print("=" * 50)
        
        try:
            from src.agent.lam_agent import LamAgent
            agent = LamAgent()
            result = agent.run(question)
            
            print("LAM Agent 回答:")
            print("=" * 50)
            print(result["answer"])
            
            if result.get("sources"):
                print("\n来源链接:")
                print("-" * 30)
                for i, source in enumerate(result["sources"], 1):
                    if source:
                        print(f"{i}. {source}")
            
            print(f"\n执行计划: {result['plan']}")
            print(f"证据数量: {result['evidence_count']}")
            
        except Exception as e:
            print(f"运行失败: {e}")

if __name__ == "__main__":
    main()






