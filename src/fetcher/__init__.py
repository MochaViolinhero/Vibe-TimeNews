# -*- coding: utf-8 -*-
"""
数据采集模块
"""

from .ai_fetcher import fetch_ai_news
from .world_fetcher import fetch_world_news
from .finance_fetcher import fetch_all as fetch_all_finance
from .github_fetcher import fetch_github_trending

__all__ = [
    "fetch_ai_news",
    "fetch_world_news",
    "fetch_all_finance",
    "fetch_github_trending",
]
