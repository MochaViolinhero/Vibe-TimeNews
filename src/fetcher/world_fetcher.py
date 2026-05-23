# -*- coding: utf-8 -*-
"""
国际新闻采集器
通过 Tavily Search API 获取最新国际新闻
"""

import os
import httpx
from typing import List, Dict

TAVILY_API_URL = "https://api.tavily.com/search"

# 首页路径模式（这些 URL 通常是新闻网站首页，不是具体文章）
HOMEPAGE_PATTERNS = [
    "/news", "/world", "/us-news", "/politics", "/business",
    "/us", "/uk", "/europe", "/asia",
]


def _is_homepage(url: str) -> bool:
    """判断 URL 是否为新闻网站首页（非具体文章）"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    # 路径为空或只有一级目录通常是首页
    if not path or path in HOMEPAGE_PATTERNS:
        return True
    # 路径只有一段且很短（如 /news, /world）
    parts = [p for p in path.split("/") if p]
    if len(parts) <= 1 and len(path) < 15:
        return True
    return False


def _is_generic_title(title: str) -> bool:
    """判断标题是否过于泛化（新闻网站名称而非文章标题）"""
    generic_phrases = [
        "breaking news", "latest news", "top stories",
        "world news", "headlines", "home page",
        "news today", "live updates",
    ]
    title_lower = title.lower()
    for phrase in generic_phrases:
        if title_lower.startswith(phrase) or title_lower.endswith(phrase):
            return True
    # 标题太短通常不是具体文章
    if len(title) < 20:
        return True
    return False


def _get_api_key() -> str:
    """从环境变量或 .env 文件获取 Tavily API Key"""
    key = os.environ.get("TAVILY_API_KEY", "")
    if key:
        return key

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TAVILY_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return ""


def fetch_world_news(max_results: int = 15) -> List[Dict]:
    """
    通过 Tavily 搜索获取最新国际新闻

    Args:
        max_results: 最多返回条数

    Returns:
        国际新闻列表
    """
    api_key = _get_api_key()
    if not api_key:
        print("[World] Tavily API Key not found")
        return []

    queries = [
        "US Iran war economy consumer sentiment May 2026",
        "Russia Ukraine conflict NATO Europe news May 2026",
        "China trade technology diplomacy news May 2026",
        "Middle East Israel Lebanon climate summit 2026",
    ]

    all_results = []
    seen_urls = set()

    for query in queries:
        try:
            payload = {
                "api_key": api_key,
                "query": query,
                "max_results": 8,
                "search_depth": "advanced",
                "include_answer": False,
                "time_range": "week",
                "exclude_domains": ["youtube.com", "instagram.com", "facebook.com", "tiktok.com"],
            }
            resp = httpx.post(TAVILY_API_URL, json=payload, timeout=20)
            if resp.status_code != 200:
                print(f"[World] Tavily error: {resp.status_code}")
                continue

            data = resp.json()
            results = data.get("results", [])

            for item in results:
                url = item.get("url", "")
                if url in seen_urls:
                    continue
                # 过滤首页链接（路径太短的通常是首页）
                if _is_homepage(url):
                    continue
                seen_urls.add(url)

                content = item.get("content", "")
                title = item.get("title", "")
                # 过滤标题过于泛化的结果
                if _is_generic_title(title):
                    continue

                all_results.append({
                    "title": title,
                    "url": url,
                    "summary": content[:200] if content else "",
                    "source": _extract_source(url),
                    "category": "world",
                })

        except Exception as e:
            print(f"[World] Tavily query failed: {e}")

    print(f"[World] Tavily: {len(all_results)} items OK")
    return all_results[:max_results]


def _extract_source(url: str) -> str:
    """从 URL 提取来源名称"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        domain = domain.replace("www.", "")
        source_map = {
            "bbc.com": "BBC",
            "bbc.co.uk": "BBC",
            "cnn.com": "CNN",
            "reuters.com": "Reuters",
            "aljazeera.com": "Al Jazeera",
            "theguardian.com": "The Guardian",
            "nytimes.com": "NYT",
            "washingtonpost.com": "Washington Post",
            "apnews.com": "AP News",
            "ndtv.com": "NDTV",
            "france24.com": "France24",
        }
        for key, name in source_map.items():
            if key in domain:
                return name
        return domain.split(".")[0].capitalize()
    except Exception:
        return "News"


if __name__ == "__main__":
    news = fetch_world_news(10)
    for n in news:
        print(f"[{n['source']}] {n['title']}")
        print(f"  {n['url']}")
        print()