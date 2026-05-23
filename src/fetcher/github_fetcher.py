# -*- coding: utf-8 -*-
"""
GitHub 热点仓库采集器
从 github.com/trending 获取今日热门项目
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_github_trending(since: str = "daily", limit: int = 15) -> List[Dict]:
    """
    获取 GitHub Trending 热门仓库

    Args:
        since: 时间范围 (daily/weekly/monthly)
        limit: 最多返回条数

    Returns:
        热门仓库列表
    """
    url = f"https://github.com/trending?since={since}"

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        if resp.status_code != 200:
            print(f"[GitHub] HTTP {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article.Box-row")

        results = []
        for article in articles[:limit]:
            # 仓库名
            h2 = article.select_one("h2 a")
            if not h2:
                continue
            repo_path = h2.get("href", "").strip("/")
            parts = repo_path.split("/")
            if len(parts) != 2:
                continue
            owner, name = parts

            # 描述
            desc_el = article.select_one("p")
            description = desc_el.text.strip() if desc_el else ""

            # 语言
            lang_el = article.select_one("[itemprop='programmingLanguage']")
            language = lang_el.text.strip() if lang_el else ""

            # 星标数（今日新增）
            stars_el = article.select("span.d-inline-block.float-sm-right")
            today_stars = ""
            if stars_el:
                today_stars = stars_el[0].text.strip()

            # 总星标
            total_stars = ""
            star_links = article.select("a.Link--muted")
            for link in star_links:
                href = link.get("href", "")
                if "/stargazers" in href:
                    total_stars = link.text.strip()
                    break

            results.append({
                "name": f"{owner}/{name}",
                "url": f"https://github.com/{owner}/{name}",
                "description": description[:120],
                "language": language,
                "stars": total_stars,
                "today_stars": today_stars,
                "category": "github",
            })

        print(f"[GitHub] Trending: {len(results)} repos OK")
        return results

    except Exception as e:
        print(f"[GitHub] Failed: {e}")
        return []


if __name__ == "__main__":
    repos = fetch_github_trending()
    for r in repos[:5]:
        print(f"  {r['name']} ({r['language']}) - {r['stars']}")
        print(f"    {r['description'][:60]}")
