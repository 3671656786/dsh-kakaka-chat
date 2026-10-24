# 对话模式 · DeepSeek Harness Agent 预设

一个面向 **DeepSeek Harness（DSH）** 的 Agent 预设：新建会话时在「模式」里选择 **对话模式**，就得到一个「对话为主、能连续多步创作」的助手——擅长**插件创作、找 bug、看日志**，并在上下文压力大时自动压缩。

> 本仓库是**独立的 DSH bundle**（不包含任何机器人框架源码）。它通过 `package.json` 的 `dsh.bundle.patch` 声明一条 `preset-chat` 预设，安装后作为 DSH 配置的一部分生效，不改动 DSH 本体。
>
> 设计蓝本是咔咔珂（kakake）的 AI 助手：把人设、工具纪律、上下文压缩策略迁移到 DSH 的 Agent 预设机制上。

## 特性

| 能力 | 实现 |
|---|---|
| 对话 / 多轮 | DSH 原生会话 + 本预设人设（结论先行、中文、带证据） |
| 插件创作 | `read` / `write` / `edit` / `glob` / `grep` + 人设里的多协议规范（`kakake-` / `GF-` / `WX-` / `ss-plugin-` / `sssx-plugin-`） |
| 找 bug / 排障 | 文件工具 + PowerShell（Windows）/ Bash（其他平台，沙箱内）+ 后台任务 + 待办 |
| 看日志 | `grep` 定位 → `read` 带 offset/limit 精读；禁止整读日志 |
| 大文件读取纪律 | `read` 单次默认且最高 **400 行**（`readLimit: 400`），先搜索后分段，禁止 `cat`/整文件读取 |
| 自动压缩上下文 | `compaction-basic`（按模型窗口比例摘要）+ `tool-result-pruner`（超大工具结果裁剪）+ `/compact` |
| plan 模式 | `plan-mode`（`/plan`）：只读调研 → `exit_plan_mode` 提交方案 → 批准后才实现 |
| 多上游模型 | 跟随会话里选的模型；可在 DSH **设置 → Models** 里加 OpenAI Chat Completions / OpenAI Responses / Anthropic Messages 兼容端点 |
| 文件变更展示 | DSH 自带 `workspace-changes` / deliverables（逐文件 diff） |
| 审计 / 技能 / 附件 | DSH 原生：JSONL 会话日志、skill 工具、`read_image` 与附件 |

## 环境要求

- **DeepSeek Harness `0.2.1-rc.3`**（本预设在该版本上验证；其它版本可能因插件包名/字段变化而失效）
- 安装 bundle 需要 **Full access 或审批**：安装会在 Host 进程里加载插件代码
- 无需 npm 依赖：所有子插件（`@deepseek-ai/dsh-*`）由 DSH 本体提供
- **Windows：必须安装 PowerShell 7（`pwsh.exe`）**。DSH 的 PowerShell 执行器在缺少 pwsh 时会回退到 Windows PowerShell 5.1，而 5.1 在 DSH 沙箱的受限令牌下启动即失败（`[exit code: 3225794]` / 0xC0000142），表现为「能改代码但跑不了校验」。安装后 DSH 会优先解析 `C:\Program Files\PowerShell\7\pwsh.exe`：

  ```powershell
  winget install --id Microsoft.PowerShell --exact --scope machine
  # GitHub 直连慢时可改用清华镜像下载 MSI 后安装：
  # https://mirrors.tuna.tsinghua.edu.cn/github-release/PowerShell/PowerShell/LatestRelease/
  ```

  装完若对话模式里 shell 仍报 0xC0000142，重启一次 DSH（执行器可能缓存了旧的 pwsh 解析）。

## 安装

### 方式一：DSH 界面安装（推荐）

在 DSH 左侧 **插件 → 添加插件**，把下面的地址粘贴进输入框，点「安装」：

```
https://github.com/3671656786/dsh-kakaka-chat
```

- 这是 **Git 地址**：DSH 会先用 `git ls-remote` 探测仓库、再用 `pnpm add` 拉取；安装后自动启用 bundle。界面上的「安装源」（npm 镜像）只对 npm 包名生效，对 Git 地址不生效。
- 安装/启用完成后：**新建会话** → Hero 区「模式」下拉 → 选 **对话模式**。
- 更新：在插件页卸载后重新安装同一地址（或按方式二用本地目录重装后重新应用）。
- 本机已验证：该地址通过 `install_bundle` 实测安装成功（`application: applied`、无 warnings、版本 0.2.1）。

### 方式二：本地目录安装（开发/离线用）

1. 克隆或下载本仓库到本地任意目录，例如：
   ```bash
   git clone https://github.com/3671656786/dsh-kakaka-chat.git
   ```
   目录里必须保留 `package.json` 与 `cordis.patch.yml`。
2. 在 DSH 会话里让 Agent 用 `plugin_manager` 安装（target 用**绝对路径**）：
   ```
   plugin_manager { action: "install_bundle", target: "C:\\path\\to\\dsh-chat-mode" }
   ```
   安装结果应为 `application: "applied"`、无 warnings。
3. 验证：
   - `plugin_manager list_plugins` 里出现 `include:preset-chat`，`fiberPhase: active`
   - **新建会话** → Hero 区「模式」下拉 → 出现 **对话模式**
4. 升级：改完目录内文件后重新 `install_bundle`，或 `set_bundle` 先关闭再开启该 bundle 让配置重新应用。已有会话保留它启动时的预设修订，新会话才用新配置。
5. 卸载：
   ```
   plugin_manager { action: "remove_bundle", target: "@local/dsh-chat-preset" }
   ```

## 使用

### 三种「本轮模式」

| 目标 | 操作 | 效果 |
|---|---|---|
| 默认（可写） | 什么都不用做（会话权限默认 `workspace-write`） | 可读写、可跑命令，写操作按审批策略询问 |
| plan（只读拟计划） | `/plan` 或输入框的计划按钮 | 只调研，`exit_plan_mode` 提交方案，批准后才实现 |
| ask（只读问答） | `/permission` 选 `read-only`，问完切回 `workspace-write` | 沙箱层拒绝写操作，只能读文件/搜索/回答 |

> DSH 没有咔咔珂那种输入框内的「本轮模式勾选」，以上是会话级切换。

### 大文件与日志读取（仿咔咔珂）

- `read` 单次默认 **400 行**，也是该会话上限（`tool-fs.readLimit: 400`），超出只返回一页并给分页脚注
- 先 `glob` 找路径、`grep` 找行号，再 `read` 带 `offset`/`limit`
- 日志排障：先 grep 错误码/连接 id/时间点，再读命中行前后 20~40 行
- shell 只允许有界读取：`tail -n`、`head -n`、`Select-String -Context`、`sed -n 'a,bp'`
- 结果被裁剪说明一次取多了：改小 `limit` 或更具体的关键词重取
- 兜底：`compaction-basic` + `tool-result-pruner` + `/compact`

需要放宽时，改 `cordis.patch.yml` 里 `tool-fs.readLimit`（400–2000），再重新应用 bundle。

### 自检与运行时探针

改完代码后助手会**自己先跑校验**（不再要求你去控制台/终端代验）：

| 检查 | 命令（工作区根目录） |
|---|---|
| 后端类型检查 | `node node_modules/typescript/bin/tsc -p tsconfig.json --noEmit` |
| 前端类型检查 | `node node_modules/typescript/bin/tsc -p src/web/tsconfig.json --noEmit` |
| 单元测试 | `node --import tsx --test --test-concurrency=1 tests/*.test.ts` |
| 单文件语法 | `node --check <文件>` |
| 启动探测 | 后台 `node --import tsx src/main.ts` → 等 10~15s → 查 `/api/status` → 停进程 |

排障时除了 `log/`，助手会主动查**咔咔珂管理 API**（服务在跑时）：

```powershell
$k=(Get-Content data/auth-key.json -Raw|ConvertFrom-Json).key
$h=@{Authorization="Bearer $k"}
Invoke-RestMethod http://127.0.0.1:8787/api/status                      # 版本/连接/插件概览（公开）
Invoke-RestMethod http://127.0.0.1:8787/api/connections -Headers $h     # 连接与在线状态
Invoke-RestMethod http://127.0.0.1:8787/api/Plugin/List -Headers $h     # 插件列表/加载状态
Invoke-RestMethod http://127.0.0.1:8787/api/system/metrics -Headers $h # CPU/内存/磁盘/运行时长
Invoke-RestMethod http://127.0.0.1:8787/api/logs -Headers $h            # 运行日志（JSON）
```

另有：`Get-Process node`、`Get-NetTCPConnection -State Listen`、`Test-NetConnection 127.0.0.1 -Port 8787`、`data/*.json`、`~/.dsh`、`%APPDATA%\@deepseek-ai\dsh-desktop\logs`。

> 密钥规则：`data/auth-key.json` 里的 key 只允许用于调用本地 API，人设禁止把它打印、复述、写进文件或提交。

### 多上游模型

预设不绑定模型。在 **设置 → Models**：
- 使用官方 DeepSeek（账号或 API Key）
- 「添加模型服务 → Custom model API」添加自定义端点：Provider ID、endpoint、协议（OpenAI Chat Completions / OpenAI Responses / Anthropic Messages）、模型列表；Key 存进 DSH credentials
- 之后在会话输入框的模型下拉里切换即可

## 结构化说明

```
dsh-chat-mode/
├── package.json        # dsh.bundle.patch 指向 cordis.patch.yml；无运行时依赖
├── cordis.patch.yml    # 插入 preset-chat：人设、工具、plan、压缩、Web、present
├── tools/
│   └── validate_preset.py   # 静态校验（结构/包名/缩进/plan-mode section）
├── .github/workflows/validate.yml  # 手动或推送时跑校验
├── README.md
└── CHANGELOG.md
```

预设内的插件（按顺序）：

| id | 插件 | 作用 |
|---|---|---|
| `persona` | `dsh-persona` | 人设与工作规范 |
| `agent-instructions` | `dsh-agent-instructions` | 读取工作区 AGENTS.md/CLAUDE.md |
| `time-context` | `dsh-time-context` | 当前时间上下文 |
| `tool-pwsh` / `tool-bash` | `dsh-tool-pwsh` / `dsh-tool-bash` | 按平台二选一 |
| `tool-fs` | `dsh-tool-fs` | read/write/edit（`readLimit: 400`） |
| `tool-fs-search` | `dsh-tool-fs-search` | glob/grep |
| `tool-jobs` | `dsh-tool-jobs` | 后台任务 |
| `skill-filesystem` / `tool-skill` | `dsh-skill-filesystem` / `dsh-tool-skill` | 技能 |
| `planning`（组） | `dsh-plan-mode` | plan 模式（**必须带非空 `section`**） |
| `compaction`（组） | `dsh-compaction-basic` / `dsh-command-compact` / `dsh-compaction-tool-result-pruner` | 自动压缩 + `/compact` + 结果裁剪 |
| `tool-ask-user` | `dsh-tool-ask-user` | 向用户提问 |
| `tool-todo` | `dsh-tool-todo` | 待办 |
| `tool-web` | `dsh-tool-web` | web_search / web_fetch |
| `present` | `dsh-tool-present` | 交付文件 |

## 故障排查

**shell 命令返回 `[exit code: 3221225794]`（0xC0000142）或「能改代码但跑不了校验」**
DSH 的 PowerShell 执行器回退到了 Windows PowerShell 5.1，它在沙箱受限令牌下起不来。安装 **PowerShell 7**（见「环境要求」）后重启 DSH 再试；仍不行可临时把会话权限切到 Full access 验证是否沙箱问题。

**「模式」卡片显示「加载失败」**
预设组合审计失败。最可靠的办法是让一个临时 Host 插件把 `agentPresets.list()` 的 `broken` 字段写出来（本仓库初版就踩过：`plan-mode.config.section` 为空 → 整份预设 broken）。其它常见原因：
- 某个子插件包名在当前 DSH 版本不存在
- 子插件缺少必需 config（如 `plan-mode.section`）
- 子插件注册了会泄漏到全局的 service（`leakedServices` 非空）

**选中后没有反应 / 还是旧行为**
已有会话保留旧预设修订：请**新建会话**再选「对话模式」。

**工具列表和预期不一致**
`plugin_manager list_plugins` 看 `include:preset-chat` 是否 active；`cordis_inspect_query` 的 `Config.listConfigs` 可按包名查挂载情况。

## 兼容性与已知限制

- 仅验证 **DSH 0.2.1-rc.3**（Desktop / Web）。DSH 升级后 `@deepseek-ai/dsh-*` 包名或字段可能变化，本 bundle 需要跟随更新。
- 人设里引用了咔咔珂（kakake）目录约定（`plugins/`、`使用教程/`、`log/` 等）；在其它项目里使用时这些指引不会自动适配，但不会报错。
- 已附 **MIT LICENSE**（GitHub 初始化仓库时生成，版权署名见 `LICENSE`）；再分发请保留版权声明。人设文本与咔咔珂相关表述的授权由维护者确认。
- 安装用 `link:` / 本地目录方式，不是 npm 包；若未来发布 npm，需改包名（去掉 `@local/`）并去掉 `"private": true`。

## 开发

```bash
# 静态校验（Python 3.9+，仅标准库）
python tools/validate_preset.py
```

校验内容：`package.json` 字段、patch 结构、插件包名白名单、缩进与 `!!js` 标签、`persona` 块标量、`plan-mode` 非空 `section`、平台 `disabled` 表达式。

## 变更记录

见 [CHANGELOG.md](CHANGELOG.md)。
