# -*- coding: utf-8 -*-
"""
数据整理层
汇总、去重、分类所有采集到的数据
"""

from typing import List, Dict, Any
from collections import defaultdict


def deduplicate(articles: List[Dict]) -> List[Dict]:
    """
    根据标题和链接去重

    Args:
        articles: 文章列表

    Returns:
        去重后的文章列表
    """
    seen_titles = set()
    seen_links = set()
    results = []

    for article in articles:
        title = article.get("title", "").strip().lower()
        link = article.get("link", "").strip().lower()

        # 跳过空标题或空链接
        if not title or not link:
            continue

        # 跳过已见过的标题或链接
        if title in seen_titles or link in seen_links:
            continue

        seen_titles.add(title)
        seen_links.add(link)
        results.append(article)

    return results


def classify(articles: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按分类标签整理文章

    Args:
        articles: 文章列表（已去重）

    Returns:
        分类后的字典 {category: [articles]}
    """
    classified = defaultdict(list)

    for article in articles:
        category = article.get("category", "other")
        classified[category].append(article)

    return dict(classified)


def aggregate(rss_articles: List[Dict], finance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    汇总所有数据，输出结构化结果

    Args:
        rss_articles: RSS 采集的文章列表
        finance_data: 财经数据（包含 indices / hot_sectors / news）

    Returns:
        汇总后的数据结构
    """
    # 去重
    deduplicated = deduplicate(rss_articles)

    # 分类
    classified = classify(deduplicated)

    result = {
        # AI 圈新闻
        "ai_news": classified.get("ai", []),
        # 国际新闻
        "world_news": classified.get("world", []),
        # 金融数据
        "finance_indices": finance_data.get("indices", []),
        "finance_sectors": finance_data.get("hot_sectors", []),
        "finance_news": finance_data.get("news", []),
        # 元信息
        "total_articles": len(deduplicated),
        "fetch_time": finance_data.get("fetch_time", ""),
    }

    return result


def format_for_display(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化数据用于 HTML 显示
    - 添加涨跌颜色标记
    - 添加趋势符号
    - 截断过长摘要
    """
    # 格式化指数数据
    for idx in data.get("finance_indices", []):
        change = idx.get("change_pct", 0)
        idx["trend"] = "up" if change >= 0 else "down"
        idx["sign"] = "+" if change >= 0 else ""

    # 格式化板块数据
    for sector in data.get("finance_sectors", []):
        change = sector.get("change_pct", 0)
        sector["trend"] = "up" if change >= 0 else "down"
        sector["sign"] = "+" if change >= 0 else ""

    # 截断金融新闻摘要
    for news in data.get("finance_news", []):
        summary = news.get("summary", "")
        if len(summary) > 120:
            news["summary"] = summary[:120] + "..."

    return data


if __name__ == "__main__":
    # 测试用模拟数据
    test_rss = [
        {"title": "AI 突破", "link": "https://example.com/1", "category": "ai"},
        {"title": "美国市场", "link": "https://example.com/2", "category": "world"},
    ]
    test_finance = {
        "indices": [{"name": "上证指数", "price": 3000, "change_pct": 1.5}],
        "hot_sectors": [{"name": "新能源", "change_pct": 2.3}],
        "news": [{"title": "财经要闻", "summary": "摘要内容..."}],
        "fetch_time": "2026-04-25 08:00:00",
    }

    result = aggregate(test_rss, test_finance)
    print("AI 新闻:", len(result["ai_news"]))
    print("国际新闻:", len(result["world_news"]))
    print("金融指数:", len(result["finance_indices"]))
    print("金融要闻:", len(result["finance_news"]))