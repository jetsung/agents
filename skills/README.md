# Agent Skills Repository

这是一个为 AI Agent 设计的技能仓库。

## 项目简介

本项目旨在收集和管理各种专门化的技能（Skills），以便在不同的 Agent 环境中复用。每个技能都包含其核心逻辑、指令和示例。

## 已包含技能

### [git-commit](./git-commit/SKILL.md)

生成遵循 Conventional Commits 规范的标准化 Git 提交消息。

- **功能**: 分析变更并生成符合规范的提交说明。
- **语言**: 提交说明（description）使用简体中文。
- **规范**: 遵循 `<type>(<scope>): <description>` 格式。

## 如何安装

使用项目根目录下的 `install.sh` 脚本可以自动将本仓库链接到各种 AI CLI 工具的 skills 目录：

```bash
./install.sh --action skills
```

### 支持的 AI Agent 工具

- Claude (`~/.claude/skills`)
- Gemini (`~/.gemini/skills`)
- OpenCode (`~/.opencode/skills`)
- Codex (`~/.codex/skills`)
- iFlow (`~/.iflow/skills`)
- Qwen (`~/.qwen/skills`)
- CodeBuddy (`~/.codebuddy/skills`)
- Cline (`~/.cline/skills`)
- Kilo Code (`~/.kilocode/skills`)
- Roo (`~/.roo/skills`)
- Factory (`~/.factory/skills`)

脚本会自动检测已安装的工具，并为每个工具创建软链接。如果目标目录已存在，脚本会自动备份。

## 如何使用

每个技能目录下的 `SKILL.md` 文件包含了该技能的详细说明和使用指令。Agent 可以根据这些指令来执行特定的任务。

## 项目结构

```
skills/
├── README.md          # 本文件
├── git-commit/        # git-commit 技能目录
│   └── SKILL.md       # 技能详细说明
└── ...                # 其他技能目录
```

## 添加新技能

1. 在 `skills/` 目录下创建新的技能目录
2. 在该目录下创建 `SKILL.md` 文件，包含技能的详细说明
3. 在 `README.md` 的「已包含技能」部分添加新技能的介绍
