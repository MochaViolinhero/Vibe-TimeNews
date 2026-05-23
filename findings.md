# Findings

## 项目当前状态

### 数据源架构（2026-05-23 重构后）
| 板块 | 数据源 | 采集方式 |
|------|--------|----------|
| AI 圈 | aihot.virxact.com | REST API（5子分类：模型/产品/行业/论文/技巧） |
| 金融圈 | 新浪财经 + 东方财富 | API + RSS |
| 国际新闻 | Tavily Search | Search API（需 TAVILY_API_KEY） |
| GitHub 热点 | github.com/trending | 页面解析 |

### 最近一次全链路测试结果
- AI 圈: 33 条
- 金融指数: 6 | 板块: 1 | 要闻: 10
- 国际新闻: 15 条
- GitHub 热点: 14 个仓库
- 总计: 72 条资讯
- 生成文件: output/daily_2026-05-23.html

### 已知问题
- 东方财富 RSS 返回 0 条（feed.eastmoney.com 可能不稳定）
- 国际新闻需要过滤首页链接，已添加 _is_homepage 和 _is_generic_title 过滤器
