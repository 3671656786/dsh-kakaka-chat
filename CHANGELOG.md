# 变更记录

## 0.3.3 — 2026-10-24

- 提示词升级为**硬性门禁**：用户未声明插件类型时先 `ask_user_question` 提问；**在用户回答之前禁止调用 `write` / `edit`** 创建或修改任何插件文件（只读操作不受限），不得先写代码再问。
- 发布方式：新增 GitHub **Release（v0.3.3）**，附更新日志与打包产物 `dsh-kakaka-chat-0.3.3.tgz`（仅离线分发，不是 npm 发布）。
- README 增加「发布版本与更新日志」章节，并同步硬性门禁说明。

## 0.3.2 — 2026-10-24

- 提示词新增：**写插件前先确认类型**——用户没声明 `kakake-` / `GF-` / `WX-` / `ss-plugin-` / `sssx-plugin-` 时，先用 `ask_user_question` 问清楚再动手，不默认猜一种直接写。
- README 增加「写插件前先确认类型」说明。

## 0.3.1 — 2026-10-24

- 提示词新增 GF-（QQ 官方机器人）铁律：群聊回复**默认带「蓝色艾特」**（content 里先 @ 触发者再写正文）；不 @ 时，机器人未开通「主动消息」权限会直接发不出去（`40034105`）。`sssx-plugin-` 双生插件走官方协议分支时同样适用。
- README 增加对应的使用提示。

## 0.3.0 — 2026-10-24

- 包名统一为 **`dsh-kakaka-chat`**（与 GitHub 仓库一致），版本 0.3.0。
- 分发方式定为 **Git 地址 / 本地目录安装**，暂不发布 npm；恢复 `"private": true` 防止误发布。
- README 更新卸载目标名（`dsh-kakaka-chat`）并注明「未发布 npm」；兼容性说明同步。

## 0.2.2 — 2026-10-24

- 文档：补充 0xC0000142 的完整根因——DSH 的 pwsh 解析结果缓存到进程退出（`dsh-pwsh-local` 的 `resolvedPwshPath`）；给出「重启 DSH」与「profile 显式 `pwshPath`（免重启）」两种修法，并在「环境要求」中同步。

## 0.2.1 — 2026-10-24

- 新增插件显示元数据：`locale/zh.json`、`locale/en.json`（`meta.title` / `meta.description`）与 `icon.svg`，在 DSH 插件页显示为「对话模式 / Chat Mode」。
- `package.json` 补充 `repository`、`exports`（`./locale/*.json`、`./icon`）与 `files`。
- README 增加「DSH 界面安装」方式：插件页 → 添加插件 → 粘贴 `https://github.com/3671656786/dsh-kakaka-chat`。
- 已用该 Git 地址实测安装成功（`application: applied`，pnpm 6.5s）。

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
