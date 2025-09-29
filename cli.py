import argparse
from src.agent.lam_agent import LamAgent


def main():
    parser = argparse.ArgumentParser(description="LAM Agent CLI")
    parser.add_argument("query", type=str, nargs='+', help="用户需求/问题")
    args = parser.parse_args()
    question = " ".join(args.query)

    agent = LamAgent()
    result = agent.run(question)
    print(result["answer"])  # noqa: T201


if __name__ == "__main__":
    main()

