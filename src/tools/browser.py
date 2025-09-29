from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from ..config import settings


def fetch_page(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 15000) -> Dict[str, Any]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.lam_browser_headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, timeout=timeout_ms)
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=timeout_ms)
        html = page.content()
        title = page.title()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    text_content = soup.get_text("\n", strip=True)
    return {"title": title, "html": html, "text": text_content}

