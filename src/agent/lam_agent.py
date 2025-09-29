from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import settings
from ..tools.search import web_search
from ..tools.browser import fetch_page


SYSTEM_PROMPT = (
    "你是一个LAM（Language + Action Model）代理。根据用户需求，合理选择：\n"
    "1) 搜索网络以获取最新信息；2) 打开页面抓取并提取要点；3) 直接回答。\n"
    "回答要准确、可执行，并在需要时给出来源链接。"
)


class LamAgent:
    def __init__(self, model: str | None = None):
        model_name = model or settings.lam_agent_model
        self.llm = ChatOpenAI(model=model_name, api_key=settings.openai_api_key, temperature=0.2)

    def run(self, user_query: str) -> Dict[str, Any]:
        plan_hint = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"用户需求：{user_query}\n先给出一步计划：是否需要搜索或抓取网页？仅回答：search / browse:<url> / answer")
        ]).content.strip()

        evidence: List[Dict[str, Any]] = []
        if plan_hint.startswith("search"):
            sr = web_search(user_query, max_results=5)
            evidence.extend(sr)
        elif plan_hint.startswith("browse:"):
            url = plan_hint.split(":", 1)[1].strip()
            page = fetch_page(url)
            evidence.append({"title": page["title"], "href": url, "body": page["text"][:4000]})

        context_text = "\n\n".join([
            f"- {item.get('title','')}\n{item.get('href','')}\n{item.get('body','')}" for item in evidence
        ])

        final = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"用户需求：{user_query}\n可用上下文：\n{context_text}\n请给出最终答案，必要时列出步骤和链接。")
        ]).content

        return {"plan": plan_hint, "evidence_count": len(evidence), "answer": final, "sources": [e.get("href") for e in evidence if e.get("href")]} 

