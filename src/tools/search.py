from duckduckgo_search import DDGS
from typing import List, Dict


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "href": r.get("href", ""),
                "body": r.get("body", ""),
            })
    return results

