# 变更记录

## 0.1.0 — 2026-10-24

首个版本（DSH 0.2.1-rc.3 验证）。

- 新增 Agent 预设 `chat`（显示名「对话模式」）：人设、工具、plan 模式、自动压缩、Web、present。
- 人设内置咔咔珂式工作规范：五类插件前缀协议规范、先读教程再动手、日志先定位后分段、密钥文件禁读、结论先行。
- 大文件读取纪律：`readLimit: 400`、先搜索后分段读、禁止整读日志、超大输出先归纳。
- 自动上下文压缩：`compaction-basic` + `tool-result-pruner` + `/compact`。
- 修复：`plan-mode` 缺少非空 `section` 导致预设被判 `broken`（UI 显示「加载失败」）。
- 新增：`tools/validate_preset.py` 静态校验与 GitHub Actions 工作流。
