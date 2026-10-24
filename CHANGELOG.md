# 变更记录

## 0.2.0 — 2026-10-24

- 新增「自检与运行时状态」规范：改完代码先自行跑后端/前端 `tsc`、单元测试、`node --check` 与启动探测，不再依赖用户手动验证。
- 新增运行时探针：通过 `data/auth-key.json` 的密钥调用咔咔珂管理 API（`/api/status`、`/api/connections`、`/api/Plugin/List`、`/api/system/metrics`、`/api/logs`），并结合进程/端口/`data/`/`~/.dsh` 排查；密钥只用于请求头，禁止打印或写入。
- 新增 0xC0000142 处置指引：先用 `pwsh` 确认版本为 7.x；仍失败则重启 DSH 或临时切 Full access；不得因执行失败跳过验证。
- 文档补充 Windows 前置：必须安装 PowerShell 7（Windows PowerShell 5.1 在 DSH 沙箱下无法启动）。

## 0.1.0 — 2026-10-24

首个版本（DSH 0.2.1-rc.3 验证）。

- 新增 Agent 预设 `chat`（显示名「对话模式」）：人设、工具、plan 模式、自动压缩、Web、present。
- 人设内置咔咔珂式工作规范：五类插件前缀协议规范、先读教程再动手、日志先定位后分段、结论先行。
- 大文件读取纪律：`readLimit: 400`、先搜索后分段读、禁止整读日志、超大输出先归纳。
- 自动上下文压缩：`compaction-basic` + `tool-result-pruner` + `/compact`。
- 修复：`plan-mode` 缺少非空 `section` 导致预设被判 `broken`（UI 显示「加载失败」）。
- 新增：`tools/validate_preset.py` 静态校验与 GitHub Actions 工作流。
