# -*- coding: utf-8 -*-
"""
财经数据采集器
使用新浪财经 API 采集 A 股指数、板块、新闻
"""

import re
import httpx
import feedparser
from datetime import datetime
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn",
}

SINA_HQ = "https://hq.sinajs.cn/list"


def _decode(text: bytes) -> str:
    """尝试用 GBK 解码，失败则用 utf-8"""
    try:
        return text.decode("gbk")
    except Exception:
        return text.decode("utf-8", errors="replace")


def _get_indices() -> List[Dict]:
    """
    获取主要 A 股指数（新浪财经 API）
    返回: [{name, price, change, change_pct}, ...]
    """
    symbols = "s_sh000001,s_sz399001,s_sz399006,s_sh000688,s_sh000300,s_sz399005"
    try:
        resp = httpx.get(f"{SINA_HQ}?list={symbols}", headers=HEADERS, timeout=15)
        text = _decode(resp.content)
        results = []
        # 格式: var hq_str_s_sh000001="name,price,change,pct,...", var hq_str_s_sz399001=...
        for match in re.finditer(r'hq_str_\w+="([^"]+)"', text):
            parts = match.group(1).split(",")
            if len(parts) < 4:
                continue
            name = parts[0]
            try:
                price = float(parts[1])
                change = float(parts[2])
                change_pct = float(parts[3])
            except (ValueError, IndexError):
                continue
            results.append({
                "name": name,
                "price": round(price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
            })
        print(f"[Finance] Index: {len(results)} OK")
        return results
    except Exception as e:
        print(f"[Finance] Index failed: {e}")
        return []


def _get_sectors() -> List[Dict]:
    """
    获取行业板块涨跌榜（新浪财经）
    返回涨幅前 10 的板块
    """
    # 新浪板块数据接口
    url = "https://vip.stock.finance.sina.com.cn/q/view/newFLJK.php"
    params = {"page": 1, "num": 10, "sort": "turnoverratio", "asc": 0, "node": "all"}
    try:
        resp = httpx.get(url, params=params, headers=HEADERS, timeout=15)
        text = _decode(resp.content)
        results = []
        # 每行格式: 代码,名称,涨跌幅,总成交量,...
        for line in text.strip().split("\n"):
            parts = line.split(",")
            if len(parts) < 4:
                continue
            try:
                results.append({
                    "name": parts[1],
                    "change_pct": round(float(parts[2]), 2),
                })
            except (ValueError, IndexError):
                continue
        print(f"[Finance] Sectors: {len(results)} OK")
        return results[:10]
    except Exception as e:
        print(f"[Finance] Sectors failed: {e}")
        return []


def _get_finance_news() -> List[Dict]:
    """
    获取金融财经要闻（新浪快讯 + 东方财富）
    返回最新财经新闻列表
    """
    results = []

    # 源1：新浪财经快讯
    sina_news_url = "https://feed.mix.sina.com.cn/api/roll/get"
    params = {"pageid": 153, "lid": 2516, "k": "", "num": 10, "page": 1}
    try:
        resp = httpx.get(sina_news_url, params=params, headers=HEADERS, timeout=15)
        data = resp.json()
        if data.get("result") and data["result"].get("data"):
            for item in data["result"]["data"][:10]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "ctime": item.get("ctime", ""),
                    "source": "新浪财经",
                    "category": "finance",
                })
        print(f"[Finance] 新浪快讯: {len(results)} OK")
    except Exception as e:
        print(f"[Finance] 新浪快讯 failed: {e}")

    # 源2：东方财富 A 股新闻 RSS
    em_news_url = "https://feed.eastmoney.com/gggsj.html"
    try:
        feed = feedparser.parse(em_news_url)
        for entry in feed.entries[:10]:
            summary = ""
            if hasattr(entry, "summary"):
                summary = re.sub(r"<[^>]+>", "", entry.summary).strip()
            if len(summary) > 150:
                summary = summary[:150] + "..."
            results.append({
                "title": entry.title.strip() if hasattr(entry, "title") else "",
                "url": entry.link if hasattr(entry, "link") else "",
                "summary": summary,
                "published": entry.get("published", ""),
                "source": "东方财富",
                "category": "finance",
            })
        print(f"[Finance] 东方财富新闻: {len(results) - sum(1 for r in results if r['source'] == '新浪财经')} OK")
    except Exception as e:
        print(f"[Finance] 东方财富新闻 failed: {e}")

    return results[:20]


def fetch_all() -> Dict[str, Any]:
    """
    采集所有财经数据

    Returns:
        dict，包含 indices / hot_sectors / news
    """
    print("[Finance] Fetching finance data...")
    indices = _get_indices()
    hot_sectors = _get_sectors()
    finance_news = _get_finance_news()

    result = {
        "indices": indices,
        "hot_sectors": hot_sectors,
        "news": finance_news,
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    total = len(indices) + len(hot_sectors) + len(finance_news)
    print(f"[Finance] Done: {total} items")
    return result


if __name__ == "__main__":
    result = fetch_all()
    print("\n--- Index ---")
    for idx in result["indices"]:
        sign = "+" if idx["change_pct"] >= 0 else ""
        print(f"  {idx['name']}: {idx['price']} ({sign}{idx['change_pct']}%)")
    print("\n--- Hot Sectors ---")
    for s in result["hot_sectors"][:5]:
        print(f"  {s['name']}: +{s['change_pct']}%")
