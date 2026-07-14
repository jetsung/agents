# AI Agents

个人 AI Agents 配置与工具仓库，用于管理和协调各种 AI 助手环境。本项目整合了多种 AI 工具的 Prompt 指令、技能（Skills）和自动化脚本，旨在提升 AI 辅助开发的效率。

## 依赖

- Python 3.x
- PyYAML (`pip install pyyaml`)
- [just](https://github.com/casey/just)（可选，用于便捷命令）

## 核心内容

- **Prompts**: 收集各主流 AI 平台（如 Anthropic, Google, OpenAI 等）的系统提示词与指令。
- **Skills**: 提供可复用的 AI 技能扩展，支持多种 AI CLI 工具。
- **Automation**: 提供便捷的跨平台安装脚本 `agents.py`，用于快速搭建和同步配置。

## 如何安装

### 使用 just（推荐）

```bash
just setup        # 完整初始化（链接目录 + 安装 skills + 安装 agents）
just setup-dir    # 仅链接当前目录到 ~/.agents
just setup-skills # 仅安装 skills 目录
just setup-agents # 仅安装 agents 配置文件
just install      # 安装所有技能
just install weiyun  # 安装指定技能
```

### 使用 Python 脚本

```bash
python3 agents.py setup        # 完整初始化
python3 agents.py setup-dir    # 仅链接目录
python3 agents.py setup-skills # 仅安装 skills
python3 agents.py setup-agents # 仅安装配置
python3 agents.py install      # 安装所有技能
python3 agents.py install weiyun  # 安装指定技能
```

## 支持的 AI 工具

| 工具 | Skills 目录 | 配置文件 |
|------|-------------|----------|
| Claude | `~/.claude/skills` | `~/.claude/CLAUDE.md` |
| OpenCode | `~/.opencode/skills` | `~/.opencode/AGENTS.md` |
| Codex | `~/.codex/skills` | `~/.codex/AGENTS.md` |
| Qwen | `~/.qwen/skills` | `~/.qwen/AGENTS.md` |
| CodeBuddy | `~/.codebuddy/skills` | `~/.codebuddy/AGENTS.md` |
| Cline | `~/.cline/skills` | `~/.cline/CLAUDE.md` |
| Roo | `~/.roo/skills` | `~/.roo/AGENTS.md` |
| Factory | `~/.factory/skills` | `~/.factory/AGENTS.md` |
| Qoder | `~/.qoder/skills` | `~/.qoder/AGENTS.md` |
| LangCLI | `~/.langcli/skills` | - |
| Gemini | - | `~/.gemini/GEMINI.md` |

脚本会自动检测已安装的工具，并为每个工具创建软链接。如果目标已存在，脚本会自动备份。

## 如何使用

每个技能目录下的 `SKILL.md` 文件包含了该技能的详细说明和使用指令。Agent 可以根据这些指令来执行特定的任务。

### just 命令

所有命令通过 `justfile` 暴露，运行 `just --list` 可查看全部配方。以下按分组列出（`<...>` 为占位参数，`[...]` 为可选）：

#### 初始化（setup 组）

| 命令 | 说明 |
|------|------|
| `just setup` | 完整初始化：链接目录 + 安装 skills + 安装 agents 配置文件 |
| `just setup dir` | 仅将当前仓库链接到 `~/.agents` |
| `just setup skills` | 仅将本项目 `skills/` 目录软链到各 AI 工具的 skills 目录 |
| `just setup agents` | 仅将 agents 配置文件软链到各 AI 工具 |
| `just setup-dir` | 同 `just setup dir` |
| `just setup-skills` | 同 `just setup skills` |
| `just setup-agents` | 同 `just setup agents` |

#### 安装工具/技能（install 组）

| 命令 | 说明 |
|------|------|
| `just install --rec` / `-r` | 安装 `config.yaml` 中 `recommended` 配置的推荐 skills |
| `just install --all` / `-a` | 安装 `config.yaml` 中 `tools` 配置的全部工具 |
| `just install <TOOLS_ID>` | 仅安装指定 `id` 的工具（如 `just install weiyun`） |
| `just init` | 同 `just install --rec` |

#### 列表（list 组）

| 命令 | 说明 |
|------|------|
| `just list skills` | 列出 `config.yaml` 中配置的 skills 渠道 |
| `just list prompts` | 列出 `config.yaml` 中配置的 prompts 渠道 |
| `just list skill` | 列出当前项目已安装的 skills |
| `just list tools` | 列出 `config.yaml` 中配置的 tools |
| `just skill-list` | 同 `just list skills` |
| `just prompt-list` | 同 `just list prompts` |

#### Skills 管理（skills 组）

| 命令 | 说明 |
|------|------|
| `just skill-show` | 显示 `config.yaml` 中所有 skills 渠道的可用 skill |
| `just skill-show <channel>` | 显示指定渠道的 skill（`<channel>` 为 config 中的 name，或 `user/repo`，或完整 URL） |
| `just skill-show --all` / `-a` | 同 `just skill-show`（列出全部渠道） |
| `just skill-query <skill>` | 跨所有渠道按名称查询单个 skill 的元信息 |
| `just skill-query <skill> <channel>` | 在指定渠道按名称查询单个 skill |
| `just skill-installed` | 列出当前项目已安装的 skills（仅名称与路径） |
| `just skill-installed --all` / `-a` | 额外展示每个 skill 的 name/description/version |
| `just skill-add <channel> <skill>` | 从指定渠道安装 skill 到项目内 `skills/` |
| `just skill-remove -a` | 删除项目内已安装的全部 skills（二次确认） |
| `just skill-remove <SKILL_PATH>` | 删除指定的单个 skill（`<SKILL_PATH>` 为 `skills/` 下的目录名，二次确认） |
| `just skill-find [query]` | 调用 `npx skills find` 搜索 skills（可带关键词） |

##### skill-show 使用说明

`skill-show` 支持以下参数形式：

| 用法 | 说明 |
|------|------|
| `just skill-show` | 显示 `config.yaml` 中所有 skills 渠道的可用 skill |
| `just skill-show antfu` | 显示 `config.yaml` 中名为 `antfu` 的渠道 |
| `just skill-show vercel-labs/agent-skills` | 直接显示 GitHub 上该仓库的 skill 列表（自动补全为 `https://github.com/...`） |
| `just skill-show https://gitlab.com/user/repo` | 通过 URL 显示任意 git 平台仓库的 skill 列表 |

> **嵌套渠道（depth）**：当某渠道在 `config.yaml` 中配置 `depth: 2`（如 `mattpocock`，布局为 `skills/<分类>/<skill>`）时，`skill-show` 会递归到两层目录，并在结果中用「路径:」标出真实相对路径（如 `engineering/grill-with-docs`）。

##### skill-add 使用说明

| 用法 | 说明 |
|------|------|
| `just skill-add antfu vue` | 单层渠道：从 `antfu` 安装 `skills/vue` |
| `just skill-add mattpocock engineering/grill-with-docs` | 嵌套渠道：传完整相对路径 `skills/<分类>/<skill>` |
| `just skill-add mattpocock grill-with-docs` | 嵌套渠道：仅传末级名，系统自动解析为 `engineering/grill-with-docs` |

> 嵌套渠道安装的 skill 落盘目录名仅取末级名（`grill-with-docs`），不带分类前缀。

##### skill-remove 使用说明

| 用法 | 说明 |
|------|------|
| `just skill-remove -a` | 删除 `skills/` 下的所有 skill（会列出数量并二次确认，默认否） |
| `just skill-remove writing-great-skills` | 删除指定的单个 skill（二次确认） |
| `just skill-remove` | 无参显示用法帮助 |

> 越界路径（如 `../foo`）会被拒绝；不存在的 skill 会提示「未找到」并以非 0 退出。`skills/` 目录本身不会被删除。

## 项目结构

```
.agents/
├── README.md           # 本文件
├── config.yaml         # 配置文件（平台、工具安装）
├── agents.py          # 跨平台安装脚本
├── justfile            # just 命令入口
├── AGENTS.md           # AI 代理行为配置
├── LICENSE             # Apache License 2.0
└── skills/
    ├── git-commit/                # git-commit 技能（来自 recommended）
    └── update-gh-action-version/  # GitHub Actions 版本更新技能
```

## 配置文件说明

配置文件 `config.yaml` 由以下顶层字段组成：`env`、`platforms`、`tools`、`skills`、`prompts`、`recommended`。

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
| `path` | string | 是 | 工具配置根目录（支持 `~` 展开），如 `~/.claude` |
| `skills` | string | 否 | 该工具下 skills 子目录名；为空则不安装 skills |
| `agents` | string | 否 | 该工具下 agents 配置文件名；为空则不安装 agents |
| `source` | string | 否 | agents 源文件名，默认为 `AGENTS.md` |

```yaml
platforms:
  claude:
    path: ~/.claude
    skills: skills
    agents: CLAUDE.md
  codebuddy:
    path: ~/.codebuddy
    skills: skills
    agents: CODEBUDDY.md
```

### tools（工具安装）

需要安装的工具/MCP 包列表，每个条目通过 `steps` 跨平台执行。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 工具唯一标识（用于 `just install <id>`） |
| `name` | string | 否 | 显示名称，默认同 `id` |
| `env` | map | 否 | 该工具专属环境变量，与全局 `env` 合并，支持 `$VAR` 替换 |
| `type` | string | 否 | 资源类型：`skill`（作为 skills 安装）或 `tool`（普通工具，默认） |
| `steps` | list | 是 | 步骤列表，每个步骤为一个命令（见下表） |

每个 `step` 可含可选 `name` 说明字段，并取以下命令之一：

| 命令 | 参数 | 说明 |
|------|------|------|
| `download` | `dest`, `extract` | 下载文件；`extract` 可为 `true`/`false` 或解压目标路径。当 `type: skill` 时缺省默认解压到 `skills/` 目录，其余情况缺省为 `true` |
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

### skills（Skills 渠道）

可供 `skill-show` / `skill-add` / `skill-query` 使用的 skill 仓库渠道。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 渠道名称（用于各 skill 命令的 `<channel>` 参数） |
| `url` | string | 是 | 仓库地址，支持 GitHub、GitLab、自建等任意 git 平台 |
| `depth` | int | 否 | skill 相对 `skills/` 的嵌套层级，默认 `1`（`skills/<skill>`）；`2` 表示 `skills/<分类>/<skill>` 两层布局 |

```yaml
skills:
  - name: antfu
    url: https://github.com/antfu/skills
  - name: mattpocock
    url: https://github.com/mattpocock/skills
    depth: 2          # 两层布局：skills/<分类>/<skill>
```

### prompts（Prompts 渠道）

与 `skills` 结构一致，用于管理各平台的 Prompt 指令源。

```yaml
prompts:
  - name: f
    url: https://github.com/f/prompts.chat
  - name: system_prompts_leaks
    url: https://github.com/asgeirtj/system_prompts_leaks
```

### recommended（推荐安装）

列出默认推荐安装的 skills，支持两种形式：

- **引用 skills 渠道**：`name`（对应 `skills[].name`）+ `skills` 列表。
- **直链仓库**：`url`（完整仓库地址）+ `skills` 列表。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 二选一 | 引用的 skills 渠道名称 |
| `url` | string | 二选一 | 直链的技能仓库地址 |
| `skills` | list | 是 | 要安装的 skill 名称列表（相对仓库 `skills/` 的路径） |

```yaml
recommended:
  - name: julianobarbosa        # 引用 skills 渠道
    skills:
      - mkdocs
  - name: myself
    url: https://git.asfd.cn/jetsung/skills.git   # 直链仓库
    skills:
      - git-commit
      - update-gh-action-version
```

## 添加新技能

1. 在 `skills/` 目录下创建新的技能目录
2. 在该目录下创建 `SKILL.md` 文件，包含技能的详细说明
3. 在 `README.md` 中添加新技能的介绍

## 许可证

[Apache License 2.0](LICENSE)

## 仓库镜像

[MyCode](https://git.jetsung.com/jetsung/agents) ● [AtomGit](https://atomgit.com/jetsung/agents) ● [GitHub](https://github.com/jetsung/agents)
