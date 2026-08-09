# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just tools install / just setup

# ==================== 工具安装 (tools) ====================

# just tools install --all / -a   安装 config.yaml 中全部 tools
# just tools install <TOOLS_ID>   仅安装指定 id 的 tool
# just tools list  --all / -a     列出全部 tools
# just tools list  <TOOLS_ID>     仅列出指定 id 的工具信息
[group('tools')]
tools *ARGS:
    #!/bin/bash
    set -- {{ARGS}}
    sub="${1:-}"; shift || true
    case "$sub" in
        install)
            uv run agents.py install "$@"
            ;;
        list)
            uv run agents.py tools-list "$@"
            ;;
        *)
            echo "用法: just tools <install|list> [--all|-a|<TOOLS_ID>]"
            exit 1
            ;;
    esac

# ==================== 平台渠道 (platforms) ====================

# 列出平台渠道（内置 + config.yaml + xskill 补充）
# just platforms           查看全部渠道
# just platforms <CHANNEL> 仅查看指定渠道
# 说明：platforms 仅一个列渠道操作，无需 list 子命令
#      （uv run agents.py platforms-list 无参数列全部，带名字列单个）
[group('platforms')]
platforms *ARGS:
    #!/bin/bash
    uv run agents.py platforms-list {{ARGS}}

# ==================== 初始化 (setup) ====================

# 安装 agents 配置文件到各 AI 工具
[group('setup')]
setup-agents:
    #!/bin/bash
    uv run agents.py setup-agents

# 完整初始化（链接 + 安装 agents）
# 支持: just setup / just setup agents
[group('setup')]
setup TARGET='':
    #!/bin/bash
    case "{{TARGET}}" in
        agents)
            uv run agents.py setup-agents
            ;;
        "")
            uv run agents.py setup
            ;;
        *)
            echo "不支持的 target: {{TARGET}}"
            echo "可用: agents"
            exit 1
            ;;
    esac
