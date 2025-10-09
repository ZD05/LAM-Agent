import argparse
import sys
import logging
from src.agent.lam_agent import LamAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """LAM Agent 命令行接口"""
    parser = argparse.ArgumentParser(
        description="LAM Agent CLI - Language + Action Model Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py "帮我查下Python 3.13 新特性"
  python cli.py "生成一个包含步骤的网页自动化示例"
  python cli.py --model gpt-4 "分析最新的AI发展趋势"
        """
    )
    parser.add_argument(
        "query", 
        type=str, 
        nargs='+', 
        help="用户需求/问题"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="指定使用的模型 (默认: 环境变量 LAM_AGENT_MODEL)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    question = " ".join(args.query)
    
    try:
        logger.info("初始化 LAM Agent...")
        agent = LamAgent(model=args.model)
        
        logger.info(f"处理查询: {question}")
        result = agent.run(question)
        
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


if __name__ == "__main__":
    main()

