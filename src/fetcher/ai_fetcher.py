# -*- coding: utf-8 -*-
"""
AI 圈新闻采集器
从 aihot.virxact.com 公开 API 获取每日 AI 新闻
分为 5 个子分类：模型、产品、行业、论文、技巧
"""

import httpx
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

AIHOT_BASE = "https://aihot.virxact.com/api/public"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 aihot-skill/0.2.0",
}

CATEGORY_MAP = {
    "ai-models": "模型发布",
    "ai-products": "产品发布",
    "industry": "行业动态",
    "paper": "论文研究",
    "tip": "技巧与观点",
}


def fetch_ai_news(hours: int = 24, take: int = 50) -> List[Dict]:
    """
    获取最近 N 小时的 AI 精选新闻

    Args:
        hours: 时间窗口（小时）
        take: 最多获取条数

    Returns:
        AI 新闻列表
    """
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{AIHOT_BASE}/items"
    params = {"mode": "selected", "since": since, "take": take}

    try:
        resp = httpx.get(url, params=params, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            print(f"[AI] aihot API error: {resp.status_code}")
            return []

        data = resp.json()
        items = data.get("items", [])
        results = []

        for item in items:
            category_slug = item.get("category", "") or ""
            category_cn = CATEGORY_MAP.get(category_slug, "其他")

            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "summary": item.get("summary", ""),
                "published": item.get("publishedAt", ""),
                "category": "ai",
                "sub_category": category_slug,
                "sub_category_cn": category_cn,
            })

        print(f"[AI] aihot: {len(results)} items OK")
        return results

    except Exception as e:
        print(f"[AI] aihot failed: {e}")
        return []