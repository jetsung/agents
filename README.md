# AI Agents

个人 AI Agents 配置与工具仓库，用于管理和协调各种 AI 助手环境。

## 项目简介

本项目旨在构建一个统一的 AI Agents 管理与配置中心，整合多种 AI 工具的配置、技能和自动化脚本，实现高效的 AI 辅助开发 workflow。

## 功能模块

### 🧠 Skills 技能系统

集中管理可复用的 AI 技能（Skills），支持多种主流 AI CLI 工具：

- **git-commit** - 生成遵循 Conventional Commits 规范的 Git 提交消息
- 更多技能持续添加中...

支持工具：Claude、Gemini、OpenCode、Codex、iFlow、Qwen、CodeBuddy、Cline、Kilo Code、Roo、Factory

### ⚙️ 配置管理

统一管理各类 AI 工具的配置文件和环境设置。

### 🚀 自动化脚本

提供便捷的安装和配置脚本，快速搭建 AI 开发环境。

## 快速开始

### 安装 Skills

```bash
./install.sh --action skills
```

脚本会自动检测已安装的 AI 工具，并将 skills 目录链接到对应位置：

- `~/.claude/skills`
- `~/.gemini/skills`
- `~/.opencode/skills`
- `~/.codex/skills`
- `~/.iflow/skills`
- `~/.qwen/skills`
- `~/.codebuddy/skills`
- `~/.cline/skills`
- `~/.kilocode/skills`
- `~/.roo/skills`
- `~/.factory/skills`

## 项目结构

```
.
├── README.md           # 项目说明（本文件）
├── install.sh          # 安装脚本
├── .gitignore          # Git 忽略配置
└── skills/             # 技能目录
    ├── README.md       # 技能系统说明
    └── git-commit/     # git-commit 技能
        └── SKILL.md    # 技能详细说明
```

## 扩展指南

### 添加新技能

1. 在 `skills/` 目录下创建新的技能目录
2. 在该目录下创建 `SKILL.md` 文件，包含技能的详细说明
3. 在 `skills/README.md` 中更新技能列表

### 添加新配置

1. 在对应目录下创建配置文件
2. 更新 `install.sh` 脚本以支持新的配置类型

## 开发计划

- [ ] 支持更多 AI 工具配置
- [ ] 添加 Agent 工作流模板
- [ ] 集成更多实用技能
- [ ] 提供配置同步功能

## 许可证

[Apache License 2.0](LICENSE)
