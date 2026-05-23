# Vibe TimeNews

每日新闻日报自动生成器 — 从多个权威信息源自动采集 AI、金融、国际新闻和 GitHub 热点，生成一份精美的深灰色极简风格 HTML 日报。

## 快速开始

```bash
# 1. 安装依赖
cd e:/Vibe-TimeNews
pip install -r requirements.txt

# 2. 配置 Tavily API Key（国际新闻采集需要）
# 编辑 src/.env 文件，填入你的 Key：
# TAVILY_API_KEY=tvly-xxx...

# 3. 运行生成日报
python src/run.py

# 4. 打开日报
# 双击 output/daily_YYYY-MM-DD.html 即可浏览
```

## 数据源

| 板块 | 来源 | 说明 |
|------|------|------|
| AI 圈 | aihot.virxact.com | 每日 AI 精选（模型/产品/行业/论文/技巧） |
| 金融圈 | 新浪财经 + 东方财富 | A股指数 + 热门板块 + 财经快讯 |
| 国际新闻 | Tavily Search API | 全球政经热点新闻 |
| GitHub 热点 | github.com/trending | 今日热门开源仓库 |

## 配置说明

### Tavily API Key

国际新闻板块依赖 Tavily Search API，需要配置 API Key：

1. 前往 [tavily.com](https://tavily.com) 注册免费账号
2. 获取 API Key
3. 写入 `src/.env` 文件：
   ```
   TAVILY_API_KEY=你的Key
   ```

### Windows 定时任务（每天 08:00 自动生成）

1. 打开「任务计划程序」（Win+R → `taskschd.msc`）
2. 创建基本任务 → 命名为「Vibe-TimeNews」
3. 触发器：每天 08:00
4. 操作：启动程序
   - 程序：`cmd`
   - 参数：`/c cd /d E:\Vibe-TimeNews && .venv\Scripts\python.exe src\run.py`
5. 完成

## 文件结构

```
e:/Vibe-TimeNews/
├── src/
│   ├── run.py              # 主入口脚本
│   ├── fetcher/
│   │   ├── ai_fetcher.py   # AI 圈（aihot API）
│   │   ├── world_fetcher.py # 国际新闻（Tavily）
│   │   ├── finance_fetcher.py # 金融数据
│   │   └── github_fetcher.py  # GitHub 热点
│   ├── aggregator.py       # 数据汇总/去重/分类
│   └── generator.py        # HTML 生成器（Jinja2）
├── output/                 # 生成的日报 HTML
├── docs/project/           # PRD + 阶段反馈
├── requirements.txt
└── scripts/run_daily.bat   # 定时任务脚本
```

## 技术栈

- Python 3.10+
- httpx（HTTP 请求）
- feedparser（RSS 解析）
- beautifulsoup4（HTML 解析）
- jinja2（模板渲染）

## 后续扩展

| 版本 | 目标 |
|------|------|
| v1.1 | 扩展更多 RSS 源（36kr、财新等） |
| v2.0 | Web 应用（FastAPI + 移动端） |
| v3.0 | 静态部署（GitHub Pages / Vercel） |
