# -*- coding: utf-8 -*-
"""
HTML 日报生成器
使用 Jinja2 模板渲染生成精美的深灰色极简日报（含波纹特效）
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, Template


# ─── 热度评分系统 ───────────────────────────────────────────────
def calc_hot_score(news: Dict, default: float = 5.0) -> float:
    """
    根据关键词出现次数估算新闻热度
    关键词越匹配分数越高，排序后热度高的在最上
    """
    title = news.get("title", "").lower()
    summary = news.get("summary", "").lower()
    text = title + " " + summary
    score = 0.0
    hot_words = [
        ("breaking", 8), ("突发", 8),
        ("热门", 5), ("hot", 5), ("爆", 6),
        ("重要", 4), ("重大", 5),
        ("最新", 3), ("刚刚", 4),
        ("暴涨", 7), ("暴跌", 7),
        ("飙升", 6), ("突破", 5),
        ("独家", 6), ("重磅", 7),
        ("升级", 3), ("发布", 2), ("推出", 2),
        ("宣布", 3), ("OpenAI", 4), ("GPT", 4),
        ("DeepSeek", 4), ("Anthropic", 4), ("Claude", 4),
        ("英伟达", 4), ("Nvidia", 4),
        ("央行", 4), ("降准", 5), ("加息", 4),
        ("峰会", 4), ("达成", 3), ("协议", 2),
    ]
    for word, weight in hot_words:
        if word.lower() in text:
            score += weight
    return score + default


def sort_by_hot(news_list: List[Dict]) -> List[Dict]:
    """按热度降序排列"""
    return sorted(news_list, key=lambda x: calc_hot_score(x), reverse=True)


# ─── 内联 Jinja2 模板（深灰色极简风格 + 波纹特效）────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css">
    <style>
        /* ─── 变量（深灰色极简） ────────────────────────────────── */
        :root {
            --bg: #1c1c1e;
            --bg-alt: #222226;
            --surface: #2a2a2e;
            --surface-hover: #38383f;
            --border: #38383e;
            --border-light: #303036;
            --text-primary: #f0f0f2;
            --text-secondary: #a1a1a6;
            --text-muted: #6e6e73;
            --up: #ff453a;
            --down: #30d158;
            --accent-finance: #ff9f0a;
            --accent-ai: #bf5af2;
            --accent-world: #64d2ff;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text-primary);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }

        /* ─── SVG 噪点滤镜 ─────────────────────────────────────── */
        .noise-bg {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
            opacity: 0.025;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        }
        .vignette {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 1;
            background: radial-gradient(ellipse at 50% 0%, transparent 0%, rgba(0,0,0,0.18) 100%);
        }

        /* ─── 头部 ─────────────────────────────────────────────── */
        .header {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(28,28,30,0.88);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
        }
        .header-inner {
            position: relative;
            z-index: 2;
            max-width: 860px;
            margin: 0 auto;
            padding: 0 32px;
        }
        .header-top {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            padding: 28px 0 20px;
            gap: 16px;
        }
        .brand-name {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.8px;
            color: var(--text-primary);
            line-height: 1;
        }
        .brand-date {
            font-size: 13px;
            font-weight: 400;
            color: var(--text-muted);
            letter-spacing: 0.2px;
        }
        .header-meta {
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 12px;
            color: var(--text-muted);
        }
        .meta-divider { width: 1px; height: 12px; background: var(--border); }

        /* ─── Tab ─────────────────────────────────────────────── */
        .tab-nav {
            display: flex;
            gap: 0;
            border-bottom: 1px solid var(--border);
        }
        .tab-btn {
            padding: 12px 24px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
            letter-spacing: 0.3px;
            display: flex;
            align-items: center;
            gap: 7px;
        }
        .tab-btn:hover { color: var(--text-secondary); }
        .tab-btn.active {
            color: var(--text-primary);
            border-bottom-color: var(--text-primary);
        }
        .tab-btn[data-tab="finance"].active { border-bottom-color: var(--accent-finance); color: var(--accent-finance); }
        .tab-btn[data-tab="ai"].active { border-bottom-color: var(--accent-ai); color: var(--accent-ai); }
        .tab-btn[data-tab="world"].active { border-bottom-color: var(--accent-world); color: var(--accent-world); }
        .tab-count {
            font-size: 11px;
            font-weight: 700;
            padding: 1px 6px;
            border-radius: 10px;
            background: var(--surface);
            color: var(--text-muted);
            line-height: 1.4;
        }

        /* ─── 主体 ─────────────────────────────────────────────── */
        .main { position: relative; z-index: 2; }
        .content-area {
            max-width: 860px;
            margin: 0 auto;
            padding: 0 32px 80px;
        }
        .panel { display: none; animation: fadeUp 0.35s ease; }
        .panel.active { display: block; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

        /* ─── 指数行 ───────────────────────────────────────────── */
        .indices-row {
            display: flex;
            gap: 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 36px;
            overflow-x: auto;
        }
        .index-item {
            display: flex;
            flex-direction: column;
            gap: 3px;
            padding: 16px 20px;
            border-right: 1px solid var(--border);
            min-width: 120px;
            flex-shrink: 0;
        }
        .index-item:last-child { border-right: none; }
        .index-name { font-size: 11px; color: var(--text-muted); font-weight: 500; letter-spacing: 0.3px; }
        .index-price { font-size: 18px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.4px; }
        .index-change { font-size: 12px; font-weight: 600; }
        .index-change.up { color: var(--up); }
        .index-change.down { color: var(--down); }

        /* ─── 板块标签 ─────────────────────────────────────────── */
        .sectors-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 32px;
        }
        .sector-tag {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.15s;
        }
        .sector-tag:hover { background: var(--surface-hover); }

        /* ─── 新闻列表 ─────────────────────────────────────────── */
        .news-list { border-top: 1px solid var(--border); }
        .news-item {
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: start;
            gap: 12px 20px;
            padding: 18px 0;
            border-bottom: 1px solid var(--border-light);
            text-decoration: none;
            color: inherit;
            transition: background 0.15s;
        }
        .news-item:last-child { border-bottom: none; }
        .news-item:hover { background: rgba(255,255,255,0.025); }
        .news-item:hover .item-title { color: #fff; }
        .item-body { min-width: 0; }
        .item-title {
            font-size: 15px;
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.55;
            transition: color 0.15s;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .item-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 6px;
            flex-wrap: wrap;
        }
        .item-source {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .item-time { font-size: 11px; color: var(--text-muted); }
        .item-title-en {
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .item-right {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
            padding-top: 2px;
            flex-shrink: 0;
        }
        .item-hot {
            display: inline-flex;
            align-items: center;
            gap: 3px;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            background: var(--surface);
            color: var(--text-muted);
            white-space: nowrap;
        }
        .item-hot.hot-high { background: rgba(255,159,10,0.15); color: var(--accent-finance); }
        .item-hot.hot-mid { background: rgba(48,209,88,0.12); color: var(--down); }
        .ext-icon {
            font-size: 14px;
            color: var(--text-muted);
            opacity: 0;
            transform: translateX(-3px);
            transition: all 0.2s;
        }
        .news-item:hover .ext-icon { opacity: 1; transform: translateX(0); }

        /* ─── 分类标题 ─────────────────────────────────────────── */
        .section-heading {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 24px 0 16px;
        }
        .section-heading span { font-size: 16px; }

        /* ─── 页脚 ─────────────────────────────────────────────── */
        footer {
            position: relative;
            z-index: 2;
            text-align: center;
            padding: 48px 32px;
            color: var(--text-muted);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }

        @media (max-width: 640px) {
            .header-inner, .content-area { padding: 0 16px; }
            .header-top { padding: 20px 0 16px; }
            .brand-name { font-size: 22px; }
            .tab-btn { padding: 10px 14px; font-size: 12px; }
            .news-item { grid-template-columns: 1fr; }
            .item-right { flex-direction: row; align-items: center; }
            .ext-icon { display: none; }
        }
    </style>
</head>
<body>
    <!-- 背景特效层 -->
    <div class="noise-bg"></div>
    <div class="vignette"></div>

    <!-- 头部 -->
    <header class="header">
        <div class="header-inner">
            <div class="header-top">
                <div>
                    <div class="brand-name">Vibe TimeNews</div>
                    <div class="brand-date">{{ date }} · Daily Briefing</div>
                </div>
                <div class="header-meta">
                    <span>共 <strong>{{ total_articles }}</strong> 条资讯</span>
                    <div class="meta-divider"></div>
                    <span>{{ fetch_time }}</span>
                </div>
            </div>

            <!-- Tab -->
            <nav class="tab-nav">
                <button class="tab-btn active" data-tab="finance" onclick="switchTab('finance')">
                    金融圈
                    <span class="tab-count" id="count-finance">{{ (finance_indices|length) + (finance_sectors|length) + (finance_news|length) }}</span>
                </button>
                <button class="tab-btn" data-tab="ai" onclick="switchTab('ai')">
                    AI 圈
                    <span class="tab-count" id="count-ai">{{ ai_news|length }}</span>
                </button>
                <button class="tab-btn" data-tab="world" onclick="switchTab('world')">
                    国际新闻
                    <span class="tab-count" id="count-world">{{ world_news|length }}</span>
                </button>
            </nav>
        </div>
    </header>

    <!-- 内容 -->
    <main class="main">
        <div class="content-area">

            <!-- ===== 金融圈 ===== -->
            <div class="panel active" id="panel-finance">

                {% if finance_indices %}
                <div class="indices-row">
                    {% for idx in finance_indices %}
                    <div class="index-item">
                        <div class="index-name">{{ idx.name }}</div>
                        <div class="index-price">{{ idx.price }}</div>
                        <div class="index-change {{ idx.trend }}">
                            {{ idx.sign }}{{ idx.change_pct }}%
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if finance_sectors %}
                <div class="sectors-wrap">
                    {% for sector in finance_sectors[:12] %}
                    <span class="sector-tag">
                        {{ sector.name }}
                        <span style="{{ 'color:var(--up)' if sector.trend=='up' else 'color:var(--down)' }}; font-weight:700;">
                            {{ sector.sign }}{{ sector.change_pct }}%
                        </span>
                    </span>
                    {% endfor %}
                </div>
                {% endif %}

                {% if finance_news %}
                <div class="section-heading"><span>💹</span> 财经要闻</div>
                <div class="news-list">
                    {% for news in finance_news[:20] %}
                    <a href="{{ news.url }}" target="_blank" rel="noopener" class="news-item">
                        <div class="item-body">
                            <div class="item-title">{{ news.title }}</div>
                            {% if news.title_en and news.title_en != news.title %}
                            <div class="item-title-en">{{ news.title_en }}</div>
                            {% endif %}
                            <div class="item-meta">
                                <span class="item-source">{{ news.source }}</span>
                                {% if news.ctime %}
                                <span class="item-time">{{ news.ctime }}</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="item-right">
                            <span class="item-hot hot-mid">● 热</span>
                            <span class="ext-icon">↗</span>
                        </div>
                    </a>
                    {% endfor %}
                </div>
                {% endif %}
            </div>

            <!-- ===== AI 圈 ===== -->
            <div class="panel" id="panel-ai">
                {% if ai_news %}
                <div class="section-heading"><span>🤖</span> AI 圈</div>
                <div class="news-list">
                    {% for news in ai_news[:20] %}
                    <a href="{{ news.link }}" target="_blank" rel="noopener" class="news-item">
                        <div class="item-body">
                            <div class="item-title">{{ news.title }}</div>
                            {% if news.title_en and news.title_en != news.title %}
                            <div class="item-title-en">{{ news.title_en }}</div>
                            {% endif %}
                            <div class="item-meta">
                                <span class="item-source">{{ news.source }}</span>
                                {% if news.published %}
                                <span class="item-time">{{ news.published }}</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="item-right">
                            <span class="item-hot hot-high">● 热门</span>
                            <span class="ext-icon">↗</span>
                        </div>
                    </a>
                    {% endfor %}
                </div>
                {% endif %}
            </div>

            <!-- ===== 国际新闻 ===== -->
            <div class="panel" id="panel-world">
                {% if world_news %}
                <div class="section-heading"><span>🌍</span> 国际新闻</div>
                <div class="news-list">
                    {% for news in world_news[:20] %}
                    <a href="{{ news.link }}" target="_blank" rel="noopener" class="news-item">
                        <div class="item-body">
                            <div class="item-title">{{ news.title }}</div>
                            {% if news.title_en and news.title_en != news.title %}
                            <div class="item-title-en">{{ news.title_en }}</div>
                            {% endif %}
                            <div class="item-meta">
                                <span class="item-source">{{ news.source }}</span>
                                {% if news.published %}
                                <span class="item-time">{{ news.published }}</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="item-right">
                            <span class="item-hot">● 最新</span>
                            <span class="ext-icon">↗</span>
                        </div>
                    </a>
                    {% endfor %}
                </div>
                {% endif %}
            </div>

        </div>
    </main>

    <footer>
        <p>Vibe TimeNews · {{ date }} · 数据来源：新浪财经 · 东方财富 · VentureBeat · BBC · CNN</p>
    </footer>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(function(b) {
                b.classList.toggle('active', b.getAttribute('data-tab') === tab);
            });
            document.querySelectorAll('.panel').forEach(function(p) {
                p.classList.toggle('active', p.getAttribute('id') === 'panel-' + tab);
            });
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
</body>
</html>"""


def generate(data: Dict[str, Any], output_dir: str = "output") -> str:
    """
    生成 HTML 日报（已按热度排序）

    Args:
        data: 聚合后的数据字典
        output_dir: 输出目录

    Returns:
        生成的 HTML 文件路径
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now()

    # ── 热度排序 ──────────────────────────────────────────────
    data["ai_news"] = sort_by_hot(data.get("ai_news", []))
    data["world_news"] = sort_by_hot(data.get("world_news", []))
    data["finance_news"] = sort_by_hot(data.get("finance_news", []))

    template_data = {
        "title": f"Vibe TimeNews 日报 · {today.strftime('%Y-%m-%d')}",
        "date": today.strftime("%Y-%m-%d"),
        "fetch_time": data.get("fetch_time", today.strftime("%Y-%m-%d %H:%M:%S")),
        "total_articles": data.get("total_articles", 0),
        "finance_indices": data.get("finance_indices", []),
        "finance_sectors": data.get("finance_sectors", []),
        "finance_news": data.get("finance_news", []),
        "ai_news": data.get("ai_news", []),
        "world_news": data.get("world_news", []),
    }

    env = Environment()
    template = env.from_string(HTML_TEMPLATE)
    html_content = template.render(**template_data)

    filename = f"daily_{today.strftime('%Y-%m-%d')}.html"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[Generator] 日报已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    test_data = {
        "ai_news": [
            {"title": "OpenAI 发布 GPT-5，性能碾压现有所有模型", "link": "https://venturebeat.com", "source": "VentureBeat", "published": "2小时前", "title_en": "OpenAI releases GPT-5", "summary": "测试摘要"},
            {"title": "Anthropic 推出 Claude 4，支持百万 Token 上下文", "link": "https://venturebeat.com", "source": "VentureBeat", "published": "4小时前"},
        ],
        "world_news": [
            {"title": "联合国安理会就中东局势召开紧急会议", "link": "https://bbc.com", "source": "BBC", "published": "1小时前"},
            {"title": "欧洲议会通过新数字法案", "link": "https://cnn.com", "source": "CNN", "published": "3小时前"},
        ],
        "finance_indices": [
            {"name": "上证指数", "price": "3245.67", "change_pct": "1.23", "trend": "up", "sign": "+"},
            {"name": "深证成指", "price": "10892.34", "change_pct": "0.87", "trend": "up", "sign": "+"},
        ],
        "finance_sectors": [
            {"name": "人工智能", "change_pct": "3.2", "trend": "up", "sign": "+"},
            {"name": "半导体", "change_pct": "2.8", "trend": "up", "sign": "+"},
        ],
        "finance_news": [
            {"title": "央行宣布定向降准 0.25 个百分点", "url": "https://finance.eastmoney.com", "source": "新浪财经", "ctime": "30分钟前", "summary": "财经摘要"},
        ],
        "total_articles": 6,
        "fetch_time": "2026-04-25 08:00:00",
    }
    path = generate(test_data)
    print(f"测试文件: {path}")
