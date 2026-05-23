# Task Plan: Vibe TimeNews 阶段6收尾

## Goal
完成 Vibe TimeNews 项目 MVP 阶段6 收尾工作，输出 README.md、验证全链路、确认 PRD 成功标准全部达成。

## Current State
- 阶段 1~5 已完成，数据源已重构为 aihot + Tavily + 新浪/东方财富 + GitHub Trending
- 四大板块 Tab 切换：金融圈 / AI 圈 / 国际新闻 / GitHub 热点
- 全链路测试通过（72 条资讯生成成功）
- PRD.md 和方案阶段反馈.md 已更新

## Phases

### Phase 1: 编写 README.md
- Status: pending
- Tasks:
  - [ ] 项目简介（一句话说明）
  - [ ] 快速开始（安装依赖 + 运行命令）
  - [ ] 配置说明（.env 中 TAVILY_API_KEY）
  - [ ] 定时任务配置指南（Windows 任务计划程序）
  - [ ] 数据源说明（4 大板块来源）
  - [ ] 文件结构说明
  - [ ] 后续扩展方向

### Phase 2: 全链路测试验证
- Status: pending
- Tasks:
  - [ ] 运行 `python src/run.py` 无报错
  - [ ] 打开生成的 HTML 验证四大板块内容
  - [ ] 验证金融指数 + 板块 + 要闻正常
  - [ ] 验证 AI 圈 5 子分类正常
  - [ ] 验证国际新闻有实际文章内容
  - [ ] 验证 GitHub 热点仓库正常
  - [ ] 验证序号标签显示正确

### Phase 3: PRD 成功标准确认
- Status: pending
- Tasks:
  - [ ] `python src/run.py` 能成功运行 → ✅
  - [ ] 日报包含 AI / 金融 / 国际 / GitHub 四大分类 → ✅
  - [ ] HTML 页面深灰色极简风格 → ✅
  - [ ] Windows 定时任务能自动运行 → ✅
  - [ ] 全程零付费 → ✅（Tavily 免费额度）

### Phase 4: 更新方案阶段反馈.md 阶段6
- Status: pending
- Tasks:
  - [ ] 标记阶段6交付物为已完成
  - [ ] 请用户填写阶段6反馈

## Decisions
- README 使用简体中文编写
- 不创建额外文档，保持精简

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| (none yet) | | |
