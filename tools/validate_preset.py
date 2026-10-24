#!/usr/bin/env python3
"""静态校验「对话模式」预设 bundle（不依赖 PyYAML，仅标准库）。

DSH 安装 bundle 时由 Cordis Loader 做权威 YAML 解析与激活；这里只做清单级检查：
JSON 字段、patch 结构、插件包名白名单、缩进/标签/块标量、plan-mode 必需 section。
CI 与本地都用 `python tools/validate_preset.py`，退出码 0 表示通过。
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCH = os.path.join(BASE, "cordis.patch.yml")

KNOWN = {
    "@deepseek-ai/dsh-agent-preset",
    "@deepseek-ai/dsh-persona",
    "@deepseek-ai/dsh-agent-instructions",
    "@deepseek-ai/dsh-time-context",
    "@deepseek-ai/dsh-tool-pwsh",
    "@deepseek-ai/dsh-tool-bash",
    "@deepseek-ai/dsh-tool-fs",
    "@deepseek-ai/dsh-tool-fs-search",
    "@deepseek-ai/dsh-tool-jobs",
    "@deepseek-ai/dsh-skill-filesystem",
    "@deepseek-ai/dsh-tool-skill",
    "@deepseek-ai/dsh-plan-mode",
    "@deepseek-ai/dsh-compaction-basic",
    "@deepseek-ai/dsh-command-compact",
    "@deepseek-ai/dsh-compaction-tool-result-pruner",
    "@deepseek-ai/dsh-tool-ask-user",
    "@deepseek-ai/dsh-tool-todo",
    "@deepseek-ai/dsh-tool-web",
    "@deepseek-ai/dsh-tool-present",
    "cordis:group",
}

errors = []


def err(msg):
    errors.append(msg)


# ---------- package.json ----------
with open(os.path.join(BASE, "package.json"), encoding="utf-8") as f:
    pkg = json.load(f)
if pkg.get("type") != "module":
    err("package.json: type 必须是 module")
pkg_name = pkg.get("name", "")
if not pkg_name:
    err("package.json: 缺少 name")
if not pkg.get("private"):
    # 准备发布到 npm 的包：需要 license / repository / semver
    if not pkg.get("license"):
        err("package.json: 可发布包应声明 license")
    if not pkg.get("repository"):
        err("package.json: 可发布包应声明 repository")
    if not re.match(r"^\d+\.\d+\.\d+", str(pkg.get("version", ""))):
        err("package.json: version 应为 semver")
patch_rel = (pkg.get("dsh") or {}).get("bundle", {}).get("patch")
if not patch_rel:
    err("package.json: 缺少 dsh.bundle.patch")
elif not os.path.exists(os.path.join(BASE, patch_rel)):
    err(f"package.json: dsh.bundle.patch 指向不存在的文件 {patch_rel}")

# ---------- cordis.patch.yml ----------
with open(PATCH, encoding="utf-8") as f:
    text = f.read()
lines = text.splitlines()

meaningful = [l for l in lines if l.strip() and not l.lstrip().startswith("#")]
if not meaningful or not meaningful[0].startswith("- insert:"):
    err("patch: 首个非注释行应为 `- insert:`")
if "\t" in text:
    err("patch: 含制表符（YAML 禁止）")
if not text.endswith("\n"):
    err("patch: 文件末尾应有换行")

name_re = re.compile(r"^\s*-?\s*name:\s*'([^']+)'\s*$")
names = []
for i, line in enumerate(lines, 1):
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    indent = len(line) - len(line.lstrip(" "))
    if indent % 2 != 0:
        err(f"patch:{i}: 缩进不是 2 的倍数：{line!r}")
    m = name_re.match(line)
    if m:
        names.append((i, m.group(1)))
    if "!!js" in line and "disabled:" not in line:
        err(f"patch:{i}: !!js 只应出现在 disabled 字段：{line!r}")

for i, name in names:
    if name not in KNOWN:
        err(f"patch:{i}: 未知插件包名 {name}")

for required in (
    "- id: preset-chat",
    "name: '@deepseek-ai/dsh-agent-preset'",
    "id: chat",
    "name: 对话模式",
):
    if required not in text:
        err(f"patch: 缺少必需内容 {required!r}")

# 块标量 prefix: |- 必须有内容且比键多缩进
key_idx = next((i for i, l in enumerate(lines) if l.strip() == "prefix: |-"), None)
if key_idx is None:
    err("patch: 缺少 persona prefix 块标量（prefix: |-）")
else:
    key_indent = len(lines[key_idx]) - len(lines[key_idx].lstrip(" "))
    body = lines[key_idx + 1:]
    indented = [l for l in body if l.strip() and (len(l) - len(l.lstrip(" "))) > key_indent]
    if len(indented) < 5:
        err("patch: persona prefix 内容过少，疑似块标量缩进错误")

# 关键能力自检
joined = " ".join(n for _, n in names)
for need in ("tool-fs", "tool-fs-search", "compaction-basic", "tool-result-pruner", "plan-mode",
             "tool-pwsh", "tool-bash", "tool-jobs", "tool-skill", "tool-ask-user", "tool-todo"):
    if need not in joined:
        err(f"缺少关键能力插件：{need}")

# 事件平台条件：pwsh / bash 各一条 disabled 表达式
if "process.platform !== 'win32'" not in text or "process.platform === 'win32'" not in text:
    err("patch: tool-pwsh / tool-bash 的平台 disabled 表达式不完整")

# 踩过的坑：preset 作用域里的 dsh-plan-mode 必须自带非空 section（不继承 Host 行的配置），
# 缺了会让整个预设被判 broken，DSH UI 显示「加载失败」。
if "name: '@deepseek-ai/dsh-plan-mode'" in text:
    idx = next(i for i, l in enumerate(lines) if "name: '@deepseek-ai/dsh-plan-mode'" in l)
    window = "\n".join(lines[idx: idx + 14])
    if "section: |" not in window or "You are in plan mode" not in window:
        err("patch: plan-mode 必须带非空 config.section（否则预设 broken，UI 显示加载失败）")

print(f"bundle: {pkg['name']} v{pkg['version']}")
print(f"patch:  {PATCH}")
print(f"lines:  {len(lines)} 行 · 插件行 {len(names)} 条")
for i, n in names:
    print(f"  line {i:>3}  {n}")
print()
if errors:
    print("FAIL")
    for e in errors:
        print("  x", e)
    sys.exit(1)
print("OK: package.json 字段、patch 结构、插件包名、缩进与标签、plan-mode section 检查全部通过")
print("（权威 YAML 解析与激活由 DSH Cordis Loader 在 install_bundle 时完成）")
