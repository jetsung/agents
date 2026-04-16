set shell := ["python3", "-c"]

# 安装 skills: just install / just install weiyun
install SKILL='':
    #!/bin/bash
    if [ -z "{{SKILL}}" ]; then
        python3 install.py --action skills
    else
        python3 install.py --action skills {{SKILL}}
    fi

# 将当前目录链接至 ~/.agents
setup-dir:
    #!/bin/bash
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    AGENTS_DIR="$HOME/.agents"

    if [ "$PROJECT_DIR" = "$AGENTS_DIR" ]; then
        echo "当前目录已在 ~/.agents，跳过链接创建。"
    elif [ -e "$AGENTS_DIR" ]; then
        if [ -L "$AGENTS_DIR" ]; then
            rm "$AGENTS_DIR"
        else
            mv "$AGENTS_DIR" "${AGENTS_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        fi
    fi
    ln -s "$PROJECT_DIR" "$AGENTS_DIR"
    echo "已链接: ~/.agents -> $PROJECT_DIR"

# 安装 skills 目录
setup-skills:
    #!/bin/bash
    AGENTS_DIR="$HOME/.agents"
    TARGETS=(
        "$HOME/.claude/skills"
        "$HOME/.opencode/skills"
        "$HOME/.codex/skills"
        "$HOME/.qwen/skills"
        "$HOME/.codebuddy/skills"
        "$HOME/.cline/skills"
        "$HOME/.roo/skills"
        "$HOME/.factory/skills"
        "$HOME/.qoder/skills"
    )

    for TARGET in "${TARGETS[@]}"; do
        if [ ! -d "$(dirname "$TARGET")" ]; then
            echo "跳过: $(dirname "$TARGET") 不存在"
            continue
        fi

        if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
            rm "$TARGET"
        fi
        ln -s "$AGENTS_DIR/skills" "$TARGET"
        echo "已链接: $TARGET -> $AGENTS_DIR/skills"
    done

# 安装 agents 配置文件
setup-agents:
    #!/bin/bash
    AGENTS_DIR="$HOME/.agents"
    TARGETS=(
        "$HOME/.gemini/GEMINI.md"
        "$HOME/.claude/CLAUDE.md"
        "$HOME/.opencode/AGENTS.md"
        "$HOME/.codex/AGENTS.md"
        "$HOME/.qwen/AGENTS.md"
        "$HOME/.codebuddy/AGENTS.md"
        "$HOME/.cline/CLAUDE.md"
        "$HOME/.kilocode/AGUDE.md"
        "$HOME/.roo/AGENTS.md"
        "$HOME/.factory/AGENTS.md"
        "$HOME/.qoder/AGENTS.md"
    )

    for TARGET in "${TARGETS[@]}"; do
        if [ ! -d "$(dirname "$TARGET")" ]; then
            echo "跳过: $(dirname "$TARGET") 不存在"
            continue
        fi

        if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
            rm "$TARGET"
        fi
        SRC_FILE="AGENTS.md"
        ln -s "$AGENTS_DIR/$SRC_FILE" "$TARGET"
        echo "已链接: $TARGET -> $AGENTS_DIR/$SRC_FILE"
    done

# 完整初始化（链接 + 安装 skills + 安装 agents）
# 支持: just setup / just setup skills / just setup agents / just setup dir
setup TARGET='':
    #!/bin/bash
    case "{{TARGET}}" in
        skills)
            just setup-skills
            ;;
        agents)
            just setup-agents
            ;;
        dir)
            just setup-dir
            ;;
        "")
            just setup-dir
            just setup-skills
            just setup-agents
            echo ""
            echo "初始化完成！"
            ;;
        *)
            echo "不支持的 target: {{TARGET}}"
            echo "可用: skills, agents, dir"
            exit 1
            ;;
    esac