#!/bin/bash

# 获取当前项目的绝对路径
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 定义 ~/.agents 目录
AGENTS_DIR="$HOME/.agents"

# 定义目标 CLI 工具的 skills 目录路径
SKILLS_TARGETS=(
    "$HOME/.claude/skills"
    "$HOME/.opencode/skills"
    "$HOME/.codex/skills"
    "$HOME/.iflow/skills"
    "$HOME/.qwen/skills"
    "$HOME/.codebuddy/skills"
    "$HOME/.cline/skills"
    "$HOME/.kilocode/skills"
    "$HOME/.roo/skills"
    "$HOME/.factory/skills"
    "$HOME/.qoder/skills"
)

# 定义目标 CLI 工具的 agents 配置文件的路径
# 格式: "目标路径:源文件相对路径"
AGENTS_TARGETS=(
    "$HOME/.claude/CLAUDE.md:AGENTS.md"
    "$HOME/.opencode/AGENTS.md:AGENTS.md"
    "$HOME/.codex/AGENTS.md:AGENTS.md"
    "$HOME/.iflow/AGENTS.md:AGENTS.md"
    "$HOME/.qwen/AGENTS.md:AGENTS.md"
    "$HOME/.codebuddy/AGENTS.md:AGENTS.md"
    "$HOME/.cline/CLAUDE.md:AGENTS.md"
    "$HOME/.kilocode/AGENTS.md:AGENTS.md"
    "$HOME/.roo/AGENTS.md:AGENTS.md"
    "$HOME/.factory/AGENTS.md:AGENTS.md"
    "$HOME/.qoder/AGENTS.md:AGENTS.md"
)

# 创建软链接的通用函数
# 参数: TARGET LINK_NAME
create_link() {
    local TARGET="$1"
    local LINK_NAME="$2"

    local PARENT_DIR="$(dirname "$LINK_NAME")"

    # 1. 检查父目录是否存在（即工具是否已安装/配置）
    if [ ! -d "$PARENT_DIR" ]; then
        echo "[跳过] 父目录不存在: $PARENT_DIR"
        return 1
    fi

    # 2. 检查目标是否已存在
    if [ -e "$LINK_NAME" ] || [ -L "$LINK_NAME" ]; then
        if [ -L "$LINK_NAME" ]; then
            # 如果是软链接，判断是否已经指向正确位置
            local CURRENT_LINK="$(readlink "$LINK_NAME")"
            if [ "$CURRENT_LINK" == "$TARGET" ]; then
                echo "[跳过] $LINK_NAME 已经是正确的软链接。"
                return 0
            else
                echo "[更新] 更新软链接: $LINK_NAME -> $TARGET"
                rm "$LINK_NAME"
            fi
        elif [ -d "$LINK_NAME" ]; then
            # 如果是真实目录，进行备份
            local BACKUP_DIR="${LINK_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
            echo "[备份] 发现现有目录，正在备份至: $BACKUP_DIR"
            mv "$LINK_NAME" "$BACKUP_DIR"
        else
            # 如果是真实文件，进行备份
            local BACKUP_FILE="${LINK_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
            echo "[备份] 发现现有文件，正在备份至: $BACKUP_FILE"
            mv "$LINK_NAME" "$BACKUP_FILE"
        fi
    fi

    # 3. 创建软链接
    if ln -s "$TARGET" "$LINK_NAME"; then
        echo "[成功] 已链接: $LINK_NAME -> $TARGET"
        return 0
    else
        echo "[失败] 无法链接: $LINK_NAME"
        return 1
    fi
}

# 安装 agents 目录的函数
install_agents_dir() {
    echo "当前项目路径: $PROJECT_DIR"
    echo "Agents 目录: $AGENTS_DIR"
    echo "开始建立软链接..."

    # 1. 检查当前目录是否在 ~/.agents 目录
    if [ "$PROJECT_DIR" = "$AGENTS_DIR" ]; then
        echo "[信息] 当前目录已在 ~/.agents，跳过链接创建。"
    else
        # 2. 如果不在，检查 ~/.agents 是否已存在
        if [ -e "$AGENTS_DIR" ]; then
            if [ -L "$AGENTS_DIR" ]; then
                # 已是软链接，检查是否指向正确位置
                local CURRENT_LINK="$(readlink "$AGENTS_DIR")"
                if [ "$CURRENT_LINK" = "$PROJECT_DIR" ]; then
                    echo "[跳过] ~/.agents 已正确链接到当前目录。"
                else
                    echo "[更新] 更新 ~/.agents 链接: $AGENTS_DIR -> $PROJECT_DIR"
                    rm "$AGENTS_DIR"
                    ln -s "$PROJECT_DIR" "$AGENTS_DIR"
                    echo "[成功] 已链接: $AGENTS_DIR -> $PROJECT_DIR"
                fi
            else
                # 是真实目录，进行备份
                local BACKUP_DIR="${AGENTS_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
                echo "[备份] 发现现有目录，正在备份至: $BACKUP_DIR"
                mv "$AGENTS_DIR" "$BACKUP_DIR"
                ln -s "$PROJECT_DIR" "$AGENTS_DIR"
                echo "[成功] 已链接: $AGENTS_DIR -> $PROJECT_DIR"
            fi
        else
            # 不存在，直接创建软链接
            ln -s "$PROJECT_DIR" "$AGENTS_DIR"
            echo "[成功] 已链接: $AGENTS_DIR -> $PROJECT_DIR"
        fi
    fi

    echo "完成！"
}

# 安装 skills 的函数
install_skills() {
    # 检查 ~/.agents 是否存在，如果不存在则自动创建
    if [ ! -e "$AGENTS_DIR" ]; then
        echo "[信息] ~/.agents 不存在，正在自动创建..."
        install_agents_dir
    fi

    echo "以 ~/.agents 为基准安装 skills..."
    echo "开始建立软链接..."

    for TARGET in "${SKILLS_TARGETS[@]}"; do
        create_link "$AGENTS_DIR/skills" "$TARGET"
    done

    echo "完成！"
}

# 安装 agents 配置文件的函数
install_agents() {
    # 检查 ~/.agents 是否存在，如果不存在则自动创建
    if [ ! -e "$AGENTS_DIR" ]; then
        echo "[信息] ~/.agents 不存在，正在自动创建..."
        install_agents_dir
    fi

    echo "以 ~/.agents 为基准安装 agents 配置文件..."
    echo "开始建立软链接..."

    for TARGET_INFO in "${AGENTS_TARGETS[@]}"; do
        # 解析目标路径和源文件
        local TARGET="${TARGET_INFO%%:*}"
        local SRC_FILE="${TARGET_INFO##*:}"

        # 检查源文件是否存在于 ~/.agents 目录
        if [ ! -f "$AGENTS_DIR/$SRC_FILE" ]; then
            echo "[跳过] 源文件不存在: $AGENTS_DIR/$SRC_FILE"
            continue
        fi

        create_link "$AGENTS_DIR/$SRC_FILE" "$TARGET"
    done

    echo "完成！"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --action ACTION    执行指定动作"
    echo "                         支持的动作:"
    echo "                           agents-dir - 将当前目录链接至 ~/.agents"
    echo "                           skills     - 安装 skills 目录"
    echo "                           agents     - 安装 agents 配置文件"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --action agents-dir - 将当前目录链接至 ~/.agents"
    echo "  $0 --action skills     - 安装 skills 目录"
    echo "  $0 --action agents     - 安装 agents 配置文件"
    echo "  $0 -a skills           - 安装 skills"
    echo "  $0 --help              - 显示帮助"
}

# 解析命令行参数
ACTION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 根据动作执行相应功能
case "$ACTION" in
    agents-dir)
        install_agents_dir
        ;;
    skills)
        install_skills
        ;;
    agents)
        install_agents
        ;;
    "")
        echo "错误: 未指定动作。请使用 --action 或 -a 指定动作。"
        show_help
        exit 1
        ;;
    *)
        echo "错误: 不支持的动作 '$ACTION'。"
        show_help
        exit 1
        ;;
esac
