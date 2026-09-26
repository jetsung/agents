# AI Agents

个人 AI Agents 配置与工具仓库，用于管理和协调各种 AI 助手环境。本项目整合了多种 AI 工具的配置文件与自动化脚本，旨在提升 AI 辅助开发的效率。

> Skills 已改用独立的 [xskill](https://github.com/jetsung/xskill) 工具管理，本仓库不再包含 skills 管理命令。

## 依赖

- [uv](https://docs.astral.sh/uv/)（Python 包管理器，用于运行脚本）
- [just](https://github.com/casey/just)（可选，用于便捷命令）

## 核心内容

- **Automation**: 提供便捷的跨平台安装脚本 `agents.py`，用于快速搭建和同步配置。
- **Tools**: 集中管理 `config.yaml` 中声明的工具/MCP 包安装。

## 如何安装

### 使用 just（推荐）

```bash
just agents all           # 分发 agents 配置到全部 AI 工具渠道
just agents claude        # 仅分发到指定渠道（slug 见 just agents 帮助）
just install -a           # 安装 config.yaml 中 tools 配置的全部工具
just install codearts     # 仅安装指定工具
```

### 使用 uv

```bash
uv run agents.py agents           # 显示 agents 分发帮助（渠道列表）
uv run agents.py agents all       # 分发 agents 配置到全部渠道
uv run agents.py agents claude    # 仅分发到指定渠道
uv run agents.py install -a       # 安装 tools 配置的全部工具
uv run agents.py install codearts # 仅安装指定工具
uv run agents.py setup            # 完整初始化（链接 + 分发配置）
uv run agents.py tools-list       # 列出全部 tools
uv run agents.py platforms-list   # 列出全部平台渠道
```

## 支持的 AI 工具渠道

| 渠道 | 配置文件 |
|------|----------|
| Claude Code | `~/.claude/CLAUDE.md` |
| OpenClaude | `~/.openclaude/CLAUDE.md` |
| OpenCode | `~/.opencode/AGENTS.md` |
| Codex | `~/.codex/AGENTS.md` |
| Command Code | `~/.commandcode/AGENTS.md` |
| DeepSeek Harness | `~/.dsh/AGENTS.md` |
| Oh My Pi | `~/.omp/agent/AGENTS.md` |
| Qwen | `~/.qwen/AGENTS.md` |
| CodeBuddy | `~/.codebuddy/CODEBUDDY.md` |
| Cline | `~/.cline/CLAUDE.md` |
| Zoo Code | `~/.roo/AGENTS.md` |
| Factory | `~/.factory/AGENTS.md` |
| Qoder | `~/.qoder/AGENTS.md` |
| Qoder CN | `~/.qoder-cn/AGENTS.md` |
| WorkBuddy | `~/.workbuddy/CODEBUDDY.md` |
| LangCLI | `~/.langcli/LANGCLI.md` |
| Antigravity | `~/.gemini/GEMINI.md` |
| AtomCode | `~/.atomcode/ATOMCODE.md` |
| Open Interpreter | `~/.openinterpreter/AGENTS.md` |
| ZCode | `~/.zcode/AGENTS.md` |
| JCode | `~/.jcode/AGENTS.md` |
| Kilo Code | `~/.kilocode/AGENTS.md` |
| Kiro | `~/.kiro/AGENTS.md` |
| Pi | `~/.pi/agent/AGENTS.md` |
| Grok Build CLI | `~/.grok/AGENTS.md` |
| MiMo Code | `~/.config/mimocode/AGENTS.md` |
| Agentty | `~/.agentty/AGENTS.md` |

渠道清单按以下三层合并，优先级由高到低（`just platforms` 可查看各渠道来源）：

1. `config.yaml` 中 `platforms` 的显式配置（可覆盖内置同名渠道）
2. `agents.py` 内置的 `BUILTIN_PLATFORMS`（默认基准，已写死全部已确认渠道）
3. `~/.xskill/settings.json` 中 `platforms` 补充的新渠道

脚本合并后为各 AI 工具创建软链接（源文件不存在时跳过）。如果目标已存在，脚本会自动备份。

## 如何使用

所有命令通过 `justfile` 暴露，运行 `just --list` 可查看全部配方。以下按分组列出（`<...>` 为占位参数，`[...]` 为可选）：

### 平台渠道（platforms 组）

| 命令 | 说明 |
|------|------|
| `just platforms` | 列出全部渠道（内置 + config.yaml + xskill 补充），含目标路径、来源与目录存在状态 |
| `just platforms <CHANNEL>` | 仅查看指定渠道 |

对应 `uv run agents.py platforms-list [<CHANNEL>]`。

### agents 配置分发（agents 组）

| 命令 | 说明 |
|------|------|
| `just agents` | 显示帮助：列出全部渠道 slug、名称与目标路径 |
| `just agents all` | 将 agents 配置文件分发（软链）到全部 AI 工具渠道 |
| `just agents <SLUG>` | 仅分发到指定渠道（如 `just agents claude`） |

### 安装工具（tools 组）

| 命令 | 说明 |
|------|------|
| `just install -a` / `--all` | 安装 `config.yaml` 中 `tools` 配置的全部工具 |
| `just install <TOOLS_ID>` | 仅安装指定 `id` 的工具（如 `just install codearts`） |
| `just list` | 列出全部 tools |
| `just list <TOOLS_ID>` | 仅列出指定 id 的工具信息 |

完整初始化（`~/.agents` 链接 + 分发配置）通过 uv 执行：`uv run agents.py setup`。

## 项目结构

```
├── README.md           # 本文件
├── config.yaml         # 配置文件（平台、工具安装）
├── config.schema.json  # config.yaml 的 JSON Schema（校验与补全）
├── agents.py           # 安装脚本（Linux shell）
├── justfile            # just 命令入口
├── AGENTS.md           # AI 代理行为配置
├── docs/               # 开发文档（SPEC.md 功能规格）
├── skills/             # type: skill 工具解压落地目录
└── LICENSE             # Apache License 2.0
```

## 配置文件说明

配置文件 `config.yaml` 由以下顶层字段组成：`env`、`platforms`、`tools`。

### env（全局环境变量）

键值对，供 `tools[].env` 与 `steps` 中通过 `$VAR` 引用替换。

```yaml
env:
  HELLO: WORLD
```

### platforms（AI 工具平台）

各 AI 工具的配置，安装时会为命中工具创建软链接。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | 是 | 工具配置根目录；支持 `~` 展开，`./` 前缀表示相对项目目录（如 `./.pi`） |
| `agents` | string | 否 | 该工具下 agents 配置文件名；为空则不安装 agents |
| `source` | string | 否 | agents 源文件名，默认为 `AGENTS.md` |
| `ensure_dir` | bool | 否 | 目标目录不存在时自动创建（默认 `false`，跳过并提示） |

```yaml
platforms:
  claude:
    path: ~/.claude
    agents: CLAUDE.md
  codebuddy:
    path: ~/.codebuddy
    agents: CODEBUDDY.md
```

> **内置渠道**：`agents.py` 的 `BUILTIN_PLATFORMS` 已写死全部已确认渠道（含 pi 的 `~/.pi/agent/AGENTS.md`），无需在 `config.yaml` 重复配置即可安装。
>
> 合并优先级：`config.yaml` 显式配置 > 内置渠道 > `~/.xskill/settings.json` 补充；通过 `just platforms` 可查看每个渠道的来源标记（`内置` / `config.yaml` / `xskill`）与目录存在状态。如需调整渠道，可在 `platforms` 中以同名渠道覆盖，或在 `~/.xskill/settings.json` 中补充新渠道。

### tools（工具安装）

需要安装的工具/MCP 包列表，每个条目通过 `steps` 执行。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 工具唯一标识（用于 `just install <id>`） |
| `name` | string | 否 | 显示名称，默认同 `id` |
| `env` | map | 否 | 该工具专属环境变量，与全局 `env` 合并，支持 `$VAR` 替换 |
| `type` | string | 否 | 资源类型：`skill` / `tool`（默认）/ `mcp` / `custom`，决定解压缺省目录与 run 工作目录 |
| `steps` | list | 是 | 步骤列表（见下） |

每个 `step` 可含可选 `name` 说明字段。`action` 与 `run` 互斥：

- **无 `action`**（默认 `shell`）→ 必须提供 `run` 字段，执行脚本
- **`action: shell`** → 同样使用 `run` 字段（`run` 必填）
- **`action` 为其他内置命令** → 使用 `source`/`target` 参数，忽略 `run` 字段（即使存在）

内置 actions：

| action | 参数 | 说明 |
|------|------|------|
| `download` | `source`(URL)，`target`(可选文件名) | 下载到 `.tmp/<id>/`；文件名缺省从 URL 提取，并导出为 `$AGENTS_ARCHIVE` |
| `extract` | `source`(可选)，`target`(可选) | 解压；`source` 省略时自动用最近一次 download 的归档名；`target` 缺省按 type（`skill`→`skills/<id>/`，`mcp`→`mcp/<id>/`）；target 已存在先移除；包内唯一顶层目录自动上提 |
| `mv` | `source`, `target` | 移动；target 已存在时先删除 |
| `cp` | `source`, `target` | 复制（目录递归） |
| `rm` | `source` | 删除文件/目录（递归） |
| `mkdir` | `source` | 创建目录（含父目录） |
| `test` | `source` + `exists`/`exists_dir`/`exists_file` | 存在性断言，不满足则退出 |
| `shell` | `run`（必填） | 使用 `run` 字段执行脚本 |

```yaml
tools:
  # MCP：下载 tgz 并解压到 mcp/codearts（包内 package/ 顶层目录自动上提）
  - id: codearts
    name: CodeArts Check MCP
    type: mcp
    env:
      URL: https://example.com/CodeArtsCheckMCP-1.0.0.tgz
    steps:
      - name: 下载
        action: download
        source: $URL
      - name: 解压到 mcp/codearts
        action: extract          # source 省略，自动用上面下载的归档名

  # Skill：下载 zip 解压到 skills/weiyun
  - id: weiyun
    name: 微云网盘技能
    type: skill
    env:
      URL: https://cdn.addon.tencentsuite.com/static/tencent-weiyun.zip
    steps:
      - action: download
        source: $URL
      - action: extract
        source: tencent-weiyun.zip

  # 工具：直接执行 shell 命令
  - id: atomcode
    name: AtomCode CLI
    type: tool
    steps:
      - name: 安装
        run: curl -fsSL https://example.com/install.sh | sh
      - name: 验证
        run: atomcode --version
```

## Skills 管理

Skills 的安装、查询与维护请使用独立的 [xskill](https://github.com/jetsung/xskill) 工具，本仓库仅通过 `tools` 配置安装少量 `type: skill` 的资源到 `skills/` 目录。

## 许可证

[Apache License 2.0](LICENSE)

## 仓库镜像

[MyCode](https://git.jetsung.com/jetsung/agents) ● [AtomGit](https://atomgit.com/jetsung/agents) ● [GitHub](https://github.com/jetsung/agents)
