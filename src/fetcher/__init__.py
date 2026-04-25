# -*- coding: utf-8 -*-
"""
数据采集模块
"""

from .rss_fetcher import fetch_rss, fetch_all as fetch_all_rss
from .finance_fetcher import fetch_all as fetch_all_finance

__all__ = [
    "fetch_rss",
    "fetch_all_rss",
    "fetch_all_finance",
]
