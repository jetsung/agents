# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just tools install / just setup

set shell := ["python3", "-c"]

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
            python3 agents.py install "$@"
            ;;
        list)
            python3 agents.py tools-list "$@"
            ;;
        *)
            echo "用法: just tools <install|list> [--all|-a|<TOOLS_ID>]"
            exit 1
            ;;
    esac

# ==================== 初始化 (setup) ====================

# 安装 agents 配置文件到各 AI 工具
[group('setup')]
setup-agents:
    #!/bin/bash
    python3 agents.py setup-agents

# 完整初始化（链接 + 安装 agents）
# 支持: just setup / just setup agents
[group('setup')]
setup TARGET='':
    #!/bin/bash
    case "{{TARGET}}" in
        agents)
            python3 agents.py setup-agents
            ;;
        "")
            python3 agents.py setup
            ;;
        *)
            echo "不支持的 target: {{TARGET}}"
            echo "可用: agents"
            exit 1
            ;;
    esac
