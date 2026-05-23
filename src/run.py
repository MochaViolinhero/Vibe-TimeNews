# -*- coding: utf-8 -*-
"""
Vibe TimeNews - 每日新闻日报生成器
主入口脚本

使用方法：
    python src/run.py
    或双击运行（Windows 任务计划程序定时触发）
"""

import sys
import os

# 设置 UTF-8 输出（解决 Windows 控制台 GBK 编码问题）
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetcher import fetch_ai_news, fetch_world_news, fetch_all_finance, fetch_github_trending
from aggregator import aggregate, format_for_display
from generator import generate


def main():
    """主流程：采集 -> 整理 -> 生成"""
    print("=" * 50)
    print("Vibe TimeNews 日报生成器")
    print("=" * 50)

    # 1. 采集 AI 圈新闻（aihot API）
    print("\n[步骤 1/5] 采集 AI 圈新闻...")
    ai_data = fetch_ai_news()
    print(f"  -> 已采集 {len(ai_data)} 条 AI 新闻")

    # 2. 采集财经数据（指数 + 板块 + 新闻）
    print("\n[步骤 2/5] 采集财经数据...")
    finance_data = fetch_all_finance()
    idx_n = len(finance_data.get("indices", []))
    sec_n = len(finance_data.get("hot_sectors", []))
    news_n = len(finance_data.get("news", []))
    print(f"  -> 指数: {idx_n} | 板块: {sec_n} | 要闻: {news_n}")

    # 3. 采集国际新闻（Tavily）
    print("\n[步骤 3/5] 采集国际新闻...")
    world_data = fetch_world_news()
    print(f"  -> 已采集 {len(world_data)} 条国际新闻")

    # 4. 采集 GitHub 热点仓库
    print("\n[步骤 4/5] 采集 GitHub 热点仓库...")
    github_data = fetch_github_trending()
    print(f"  -> 已采集 {len(github_data)} 个热门仓库")

    # 5. 数据汇总 + 生成 HTML
    print("\n[步骤 5/5] 数据整理 + 生成 HTML...")
    aggregated = aggregate(ai_data, world_data, finance_data, github_data)
    formatted = format_for_display(aggregated)
    output_path = generate(formatted)

    total = len(ai_data) + len(world_data) + news_n + len(github_data)
    print(f"  -> 日报已保存: {output_path}")

    print("\n" + "=" * 50)
    print(f"[OK] 生成完成！共 {total} 条资讯")
    print(f"[FILE] {output_path}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[WARN] 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
