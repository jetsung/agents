# AI Agents

个人 AI Agents 配置与工具仓库，用于管理和协调各种 AI 助手环境。本项目整合了多种 AI 工具的 Prompt 指令、技能（Skills）和自动化脚本，旨在提升 AI 辅助开发的效率。

## 依赖

- Python 3.x
- PyYAML (`pip install pyyaml`)
- [just](https://github.com/casey/just)（可选，用于便捷命令）

## 核心内容

- **Prompts**: 收集各主流 AI 平台（如 Anthropic, Google, OpenAI 等）的系统提示词与指令。
- **Skills**: 提供可复用的 AI 技能扩展，支持多种 AI CLI 工具。
- **Automation**: 提供便捷的跨平台安装脚本 `install.py`，用于快速搭建和同步配置。

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
python3 install.py setup        # 完整初始化
python3 install.py setup-dir    # 仅链接目录
python3 install.py setup-skills # 仅安装 skills
python3 install.py setup-agents # 仅安装配置
python3 install.py install      # 安装所有技能
python3 install.py install weiyun  # 安装指定技能
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

## 项目结构

```
.agents/
├── README.md           # 本文件
├── config.yaml         # 配置文件（平台、工具安装）
├── install.py          # 跨平台安装脚本
├── justfile            # just 命令入口
├── AGENTS.md           # AI 代理行为配置
├── LICENSE             # Apache License 2.0
└── skills/
    ├── git-commit/     # git-commit 技能
    └── update-gh-action-version/  # GitHub Actions 版本更新
```

## 配置文件说明

配置文件 `config.yaml` 包含以下部分：

```yaml
# 环境变量（全局）
env:
  HELLO: WORLD

# 工具平台配置
platforms:
  claude:
    path: ~/.claude
    skills: skills
    agents: CLAUDE.md

# 技能安装配置
tools:
  - id: weiyun
    name: 微云 MCP 工具
    env:
      URL: https://example.com/tool.zip
    steps:
      - download: $URL
        dest: tool.zip
        extract: skills  # 可选，默认 true
```

### steps 支持的命令

| 命令 | 参数 | 说明 |
|------|------|------|
| `download` | `dest`, `extract` | 下载文件，可选自动解压 |
| `unzip` | `src`, `dest` | 解压 zip 文件（已弃用） |
| `copy` | `src`, `dest` | 复制文件/目录 |
| `move` | `src`, `dest` | 移动文件/目录 |
| `mkdir` | `path` | 创建目录 |
| `remove` | `path` | 删除文件/目录 |

## 添加新技能

1. 在 `skills/` 目录下创建新的技能目录
2. 在该目录下创建 `SKILL.md` 文件，包含技能的详细说明
3. 在 `README.md` 中添加新技能的介绍

## 许可证

[Apache License 2.0](LICENSE)

## 仓库镜像

[MyCode](https://git.jetsung.com/jetsung/agents) ● [AtomGit](https://atomgit.com/jetsung/agents) ● [GitHub](https://github.com/jetsung/agents)
