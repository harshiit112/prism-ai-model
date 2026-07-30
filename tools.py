import os
from typing import Any, Callable

try:
    from langchain.tools import tool
except Exception:  # pragma: no cover - fallback for older/newer langchain versions
    def tool(func: Callable[..., Any] | None = None, *args: Any, **kwargs: Any):
        if func is None:
            return lambda f: f
        return func

try:
    import requests
except Exception:  # pragma: no cover - environment fallback
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - environment fallback
    BeautifulSoup = None

try:
    from tavily import TavilyClient
except Exception:  # pragma: no cover - environment fallback
    TavilyClient = None

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - environment fallback
    def load_dotenv() -> bool:
        return False

load_dotenv()


def _build_tavily_client():
    if TavilyClient is None:
        return None
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    try:
        return TavilyClient(api_key=api_key)
    except Exception:
        return None


tavily = _build_tavily_client()


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    if tavily is None:
        return (
            f"Web search is unavailable in this environment. "
            f"Please provide a manual summary for: {query}"
        )

    try:
        results = tavily.search(query=query, max_results=5)
    except Exception as exc:
        return f"Could not search the web: {exc}"

    out = []
    for r in results.get("results", []):
        content = r.get("content", "")
        out.append(
            f"Title: {r.get('title', 'Untitled')}\n"
            f"URL: {r.get('url', 'No URL')}\n"
            f"Snippet: {content[:300]}\r"
        )

    return "\n----\n".join(out) if out else "No search results found."


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    if requests is None or BeautifulSoup is None:
        return f"Web scraping is unavailable in this environment for URL: {url}"

    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as exc:
        return f"Could not scrape URL: {exc}"


