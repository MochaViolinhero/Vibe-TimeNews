# -*- coding: utf-8 -*-
"""
RSS 采集器
从 VentureBeat AI / BBC World / CNN World 采集新闻
"""

import re
import httpx
import feedparser
from datetime import datetime
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# 英文标题翻译词典（常见词汇映射）
TITLE_TRANSLATIONS = {
    # AI / 科技
    "AI": "人工智能",
    "artificial intelligence": "人工智能",
    "machine learning": "机器学习",
    "deep learning": "深度学习",
    "neural network": "神经网络",
    "LLM": "大语言模型",
    "OpenAI": "OpenAI",
    "Microsoft": "微软",
    "Google": "谷歌",
    "Meta": "Meta",
    "Apple": "苹果",
    "Amazon": "亚马逊",
    "Nvidia": "英伟达",
    "startup": "创业公司",
    "tech": "科技",
    "technology": "科技",
    "software": "软件",
    "hardware": "硬件",
    "chip": "芯片",
    "semiconductor": "半导体",
    "cloud": "云",
    "data": "数据",
    "algorithm": "算法",
    "robot": "机器人",
    "automation": "自动化",
    "cyber": "网络",
    "security": "安全",
    "privacy": "隐私",
    # 财经 / 市场
    "stock": "股票",
    "market": "市场",
    "trading": "交易",
    "investment": "投资",
    "economy": "经济",
    "economic": "经济",
    "growth": "增长",
    "recession": "衰退",
    "inflation": "通胀",
    "interest rate": "利率",
    "fed": "美联储",
    "federal reserve": "美联储",
    "bank": "银行",
    "finance": "金融",
    "financial": "金融",
    "currency": "货币",
    "dollar": "美元",
    "yuan": "人民币",
    "yuan": "元",
    "bond": "债券",
    "oil": "石油",
    "energy": "能源",
    "gold": "黄金",
    # 国际 / 政治
    "china": "中国",
    "chinese": "中国",
    "us": "美国",
    "united states": "美国",
    "america": "美国",
    "american": "美国",
    "europe": "欧洲",
    "european": "欧洲",
    "uk": "英国",
    "russia": "俄罗斯",
    "ukraine": "乌克兰",
    "middle east": "中东",
    "asia": "亚洲",
    "asia-pacific": "亚太",
    "trade": "贸易",
    "war": "战争",
    "conflict": "冲突",
    "election": "选举",
    "politics": "政治",
    "government": "政府",
    "president": "总统",
    "summit": "峰会",
    "deal": "协议",
    "agreement": "协议",
    # 动作 / 状态
    "announces": "宣布",
    "announced": "已宣布",
    "launches": "发布",
    "launched": "已发布",
    "unveils": "推出",
    "unveiled": "已推出",
    "reveals": "揭示",
    "revealed": "已揭示",
    "reports": "报道",
    "says": "表示",
    "wins": "赢得",
    "buys": "收购",
    "sells": "出售",
    "merger": "合并",
    "acquisition": "收购",
    "partnership": "合作",
    "deal": "交易",
    "crash": "暴跌",
    "soars": "暴涨",
    "drops": "下跌",
    "rises": "上涨",
    "gains": "上涨",
    "loses": "下跌",
    # 时间
    "today": "今日",
    "yesterday": "昨日",
    "this week": "本周",
    "this month": "本月",
    "new": "新",
    "latest": "最新",
    "breaking": "突发",
    "update": "更新",
}


def _translate_title(title: str) -> str:
    """
    将英文标题翻译成中文（规则化处理 + 词典映射）
    保留英文原文供用户参考
    """
    result = title

    # 按关键词长度降序替换（避免短词先匹配导致长词无法匹配）
    sorted_keys = sorted(TITLE_TRANSLATIONS.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        result = pattern.sub(TITLE_TRANSLATIONS[key], result)

    # 清理多余空格
    result = re.sub(r'\s+', ' ', result).strip()

    # 如果翻译后内容与原文基本相同（未匹配到任何词），添加英文标注
    if result == title:
        return title  # 保留原文
    return result


# RSS 数据源配置
RSS_SOURCES = {
    "ai": {
        "name": "VentureBeat AI",
        "short_name": "VentureBeat",
        "url": "https://venturebeat.com/feed",
        "category": "ai",
        "icon": "🤖",
    },
    "bbc": {
        "name": "BBC World News",
        "short_name": "BBC",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "world",
        "icon": "🌍",
    },
    "cnn": {
        "name": "CNN World",
        "short_name": "CNN",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
        "category": "world",
        "icon": "🌍",
    },
}


def _fetch_feed_text(url: str) -> str:
    """用 httpx 获取 RSS 内容（跟随重定向），失败则降级用 feedparser"""
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        pass
    # 降级：直接用 feedparser parse（它会自己处理）
    return url  # feedparser.parse 接受 URL 字符串


def fetch_rss(source_key: str) -> List[Dict]:
    """
    采集指定 RSS 源的文章列表

    Args:
        source_key: RSS_SOURCES 中的键名（ai / bbc / cnn）

    Returns:
        文章列表，每条为 dict，包含 title / link / summary / published / source
    """
    source = RSS_SOURCES.get(source_key)
    if not source:
        print(f"[RSS] Unknown source: {source_key}")
        return []

    try:
        feed_text = _fetch_feed_text(source["url"])
        feed = feedparser.parse(feed_text)
        articles = []

        for entry in feed.entries[:15]:  # 最多取 15 条
            # 提取摘要，过滤 HTML 标签
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description
            summary = re.sub(r"<[^>]+>", "", summary).strip()
            # 截断到 200 字
            if len(summary) > 200:
                summary = summary[:200] + "..."

            # 发布时间
            published = ""
            if hasattr(entry, "published"):
                try:
                    dt = datetime(*entry.published_parsed[:6])
                    published = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    published = entry.published

            # 原文标题 + 中文翻译标题
            original_title = entry.title.strip() if hasattr(entry, "title") else ""
            translated_title = _translate_title(original_title)

            article = {
                "title": translated_title if translated_title != original_title else original_title,
                "title_en": original_title if translated_title != original_title else "",
                "link": entry.link if hasattr(entry, "link") else "",
                "summary": summary,
                "published": published,
                "source": source["short_name"],
                "source_name": source["name"],
                "source_icon": source["icon"],
                "category": source["category"],
            }
            articles.append(article)

        print(f"[RSS] {source['name']} -> {len(articles)} articles")
        return articles

    except Exception as e:
        print(f"[RSS] {source['name']} 采集失败: {e}")
        return []


def fetch_all() -> List[Dict]:
    """
    采集所有 RSS 源的文章

    Returns:
        所有来源的文章列表
    """
    all_articles = []
    for source_key in RSS_SOURCES:
        articles = fetch_rss(source_key)
        all_articles.extend(articles)
    print(f"[RSS] Total: {len(all_articles)} articles")
    return all_articles


if __name__ == "__main__":
    # 单独测试：运行 python src/fetcher/rss_fetcher.py
    articles = fetch_all()
    for a in articles[:3]:
        print(f"  [{a['source']}] {a['title']}")
