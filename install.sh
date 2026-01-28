#!/bin/bash

# 获取当前项目的绝对路径
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 定义目标 CLI 工具的 skills 目录路径
# 可以在这里添加更多工具
TARGETS=(
    "$HOME/.claude/skills"
    "$HOME/.gemini/skills"
    "$HOME/.opencode/skills"
    "$HOME/.codex/skills"
    "$HOME/.iflow/skills"
    "$HOME/.qwen/skills"
    "$HOME/.codebuddy/skills"
    "$HOME/.cline/skills"
    "$HOME/.kilocode/skills"
    "$HOME/.roo/skills"
    "$HOME/.factory/skills"
)

# 安装 skills 的函数
install_skills() {
    echo "当前项目路径: $PROJECT_DIR"
    echo "开始建立软链接..."

    for TARGET in "${TARGETS[@]}"; do
        PARENT_DIR="$(dirname "$TARGET")"

        # 1. 检查父目录是否存在（即工具是否已安装/配置）
        if [ ! -d "$PARENT_DIR" ]; then
            echo "[跳过] 父目录不存在: $PARENT_DIR"
            continue
        fi

        # 2. 检查目标是否已存在
        if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
            if [ -L "$TARGET" ]; then
                # 如果是软链接，判断是否已经指向正确位置
                CURRENT_LINK="$(readlink "$TARGET")"
                if [ "$CURRENT_LINK" == "$PROJECT_DIR/skills" ]; then
                    echo "[跳过] $TARGET 已经是正确的软链接。"
                    continue
                else
                    echo "[更新] 更新软链接: $TARGET -> $PROJECT_DIR/skills"
                    rm "$TARGET"
                fi
            elif [ -d "$TARGET" ]; then
                # 如果是真实目录，进行备份
                BACKUP_DIR="${TARGET}_backup_$(date +%Y%m%d_%H%M%S)"
                echo "[备份] 发现现有目录，正在备份至: $BACKUP_DIR"
                mv "$TARGET" "$BACKUP_DIR"
            else
                # 如果是文件（非目录非链接），也备份
                 BACKUP_FILE="${TARGET}_backup_$(date +%Y%m%d_%H%M%S)"
                 echo "[备份] 发现现有文件，正在备份至: $BACKUP_FILE"
                 mv "$TARGET" "$BACKUP_FILE"
            fi
        fi

        # 3. 创建软链接
        if ln -s "$PROJECT_DIR/skills" "$TARGET"; then
            echo "[成功] 已链接: $TARGET -> $PROJECT_DIR/skills"
        else
            echo "[失败] 无法链接: $TARGET"
        fi
    done

    echo "完成！"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --action ACTION    执行指定动作"
    echo "                         支持的动作: skills (安装 skills)"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --action skills     安装 skills"
    echo "  $0 -a skills           安装 skills"
    echo "  $0 --help              显示帮助"
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
if [ "$ACTION" == "skills" ]; then
    install_skills
elif [ -z "$ACTION" ]; then
    echo "错误: 未指定动作。请使用 --action 或 -a 指定动作。"
    show_help
    exit 1
else
    echo "错误: 不支持的动作 '$ACTION'。"
    show_help
    exit 1
fi
