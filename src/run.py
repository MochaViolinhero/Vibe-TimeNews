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

from fetcher import fetch_all_rss, fetch_all_finance
from aggregator import aggregate, format_for_display
from generator import generate


def safe_print(msg):
    """安全打印（处理编码问题）"""
    try:
        print(msg)
    except Exception:
        print(msg.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))


def main():
    """主流程：采集 → 整理 → 生成"""
    print("=" * 50)
    print("Vibe TimeNews 日报生成器")
    print("=" * 50)

    # 1. 采集 RSS 新闻（AI + 国际）
    print("\n[步骤 1/4] 采集 RSS 新闻...")
    rss_data = fetch_all_rss()
    print(f"  → 已采集 {len(rss_data)} 条 RSS 文章")

    # 2. 采集财经数据（指数 + 板块 + 新闻）
    print("\n[步骤 2/4] 采集财经数据...")
    finance_data = fetch_all_finance()
    indices_count = len(finance_data.get("indices", []))
    sectors_count = len(finance_data.get("hot_sectors", []))
    news_count = len(finance_data.get("news", []))
    print(f"  → 指数: {indices_count} | 板块: {sectors_count} | 财经要闻: {news_count}")

    # 3. 数据汇总 + 整理
    print("\n[步骤 3/4] 数据整理...")
    aggregated = aggregate(rss_data, finance_data)
    formatted = format_for_display(aggregated)
    print(f"  → AI新闻: {len(formatted['ai_news'])} | 国际新闻: {len(formatted['world_news'])} | 金融要闻: {len(formatted['finance_news'])}")

    # 4. 生成 HTML 日报
    print("\n[步骤 4/4] 生成 HTML 日报...")
    output_path = generate(formatted)
    print(f"  → 日报已保存: {output_path}")

    print("\n" + "=" * 50)
    print(f"[OK] 生成完成！共 {formatted['total_articles']} 条资讯")
    print(f"[FILE] 日报已保存: {output_path}")
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
        print(f"\n\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)