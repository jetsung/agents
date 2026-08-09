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
just setup                # 完整初始化（链接目录 + 安装 agents）
just setup-agents         # 仅安装 agents 配置文件
just tools install --all  # 安装 config.yaml 中 tools 配置的全部工具
just tools install weiyun # 仅安装指定工具
```

### 使用 uv

```bash
uv run agents.py setup            # 完整初始化
uv run agents.py setup-agents     # 仅安装配置
uv run agents.py install          # 安装 tools 配置的全部工具
uv run agents.py install weiyun   # 仅安装指定工具
uv run agents.py tools-list       # 列出全部 tools
```

## 支持的 AI 工具

| 工具 | 配置文件 |
|------|----------|
| Claude | `~/.claude/CLAUDE.md` |
| OpenClaude | `~/.openclaude/CLAUDE.md` |
| OpenCode | `~/.opencode/AGENTS.md` |
| Codex | `~/.codex/AGENTS.md` |
| Qwen | `~/.qwen/AGENTS.md` |
| CodeBuddy | `~/.codebuddy/CODEBUDDY.md` |
| Cline | `~/.cline/CLAUDE.md` |
| Roo | `~/.roo/AGENTS.md` |
| Factory | `~/.factory/AGENTS.md` |
| Qoder | `~/.qoder/AGENTS.md` |
| LangCLI | - |
| Pi（全局） | `~/.pi/agent/AGENTS.md` |
| Gemini | `~/.gemini/GEMINI.md` |
| AtomCode | `~/.atomcode/ATOMCODE.md` |

脚本会按 `config.yaml` 中 `platforms` 的配置为各 AI 工具创建软链接（源文件不存在时跳过）。如果目标已存在，脚本会自动备份。

## 如何使用

所有命令通过 `justfile` 暴露，运行 `just --list` 可查看全部配方。以下按分组列出（`<...>` 为占位参数，`[...]` 为可选）：

### 初始化（setup 组）

| 命令 | 说明 |
|------|------|
| `just setup` | 完整初始化：链接目录 + 安装 agents 配置文件 |
| `just setup agents` | 仅将 agents 配置文件软链到各 AI 工具 |

### 安装工具（tools 组）

| 命令 | 说明 |
|------|------|
| `just tools install --all` / `-a` | 安装 `config.yaml` 中 `tools` 配置的全部工具 |
| `just tools install <TOOLS_ID>` | 仅安装指定 `id` 的工具（如 `just tools install weiyun`） |
| `just tools list` | 列出全部 tools |
| `just tools list <TOOLS_ID>` | 仅列出指定 id 的工具信息 |

## 项目结构

```
├── README.md           # 本文件
├── config.yaml         # 配置文件（平台、工具安装）
├── config.schema.json  # config.yaml 的 JSON Schema（校验与补全）
├── agents.py           # 跨平台安装脚本
├── justfile            # just 命令入口
├── AGENTS.md           # AI 代理行为配置
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

> **内置渠道**：pi 渠道（全局 `~/.pi/agent/AGENTS.md`）已写死在 `agents.py` 的 `BUILTIN_PLATFORMS`，无需在 `config.yaml` 配置。如需调整行为，可在 `platforms` 中以同名 `pi` 覆盖，或新增其它自定义渠道。

### tools（工具安装）

需要安装的工具/MCP 包列表，每个条目通过 `steps` 跨平台执行。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 工具唯一标识（用于 `just tools install <id>`） |
| `name` | string | 否 | 显示名称，默认同 `id` |
| `env` | map | 否 | 该工具专属环境变量，与全局 `env` 合并，支持 `$VAR` 替换 |
| `type` | string | 否 | 资源类型：`skill`（作为 skill 解压到项目内 `skills/` 目录）或 `tool`（普通工具，默认） |
| `steps` | list | 是 | 步骤列表，每个步骤为一个命令（见下表） |

每个 `step` 可含可选 `name` 说明字段，并取以下命令之一：

| 命令 | 参数 | 说明 |
|------|------|------|
| `download` | `dest`, `extract` | 下载文件；`extract` 缺省为 `true`（解压到 `skills/` 目录），也可为 `false` 或指定解压路径 |
| `run` | — | 直接执行 shell 命令字符串（类似 GitHub Actions 的 `run:`） |
| `unzip` | `src`, `dest` | 解压 zip 文件（已弃用，建议用 `download` + `extract`） |
| `copy` | `src`, `dest` | 复制文件/目录 |
| `move` | `src`, `dest` | 移动文件/目录 |
| `mkdir` | `path` | 创建目录 |
| `remove` | `path` | 删除文件/目录 |

```yaml
tools:
  - id: weiyun
    name: 微云网盘 MCP 技能
    type: skill
    env:
      URL: https://cdn.addon.tencentsuite.com/static/tencent-weiyun.zip
    steps:
      - name: 下载微云网盘 MCP 技能
        download: $URL
        dest: tencent-weiyun.zip
      - name: 确保落地到 skills/weiyun
        run: test -d skills/weiyun || mv skills/* skills/weiyun 2>/dev/null || true
```

## Skills 管理

Skills 的安装、查询与维护请使用独立的 [xskill](https://github.com/jetsung/xskill) 工具，本仓库仅通过 `tools` 配置安装少量 `type: skill` 的资源到 `skills/` 目录。

## 许可证

[Apache License 2.0](LICENSE)

## 仓库镜像

[MyCode](https://git.jetsung.com/jetsung/agents) ● [AtomGit](https://atomgit.com/jetsung/agents) ● [GitHub](https://github.com/jetsung/agents)
