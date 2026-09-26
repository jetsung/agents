# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just install / just list / just agents

# ==================== 工具安装 ====================

# just install --all / -a   安装 config.yaml 中全部 tools
# just install <TOOLS_ID>   仅安装指定 id 的 tool
[group('tools')]
install *ARGS:
    #!/bin/bash
    uv run agents.py install {{ARGS}}

# just list --all / -a      列出全部 tools
# just list <TOOLS_ID>      仅列出指定 id 的工具信息
[group('tools')]
list *ARGS:
    #!/bin/bash
    uv run agents.py tools-list {{ARGS}}

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

# ==================== agents 配置分发 ====================

# just agents               显示帮助（列出全部平台渠道 slug）
# just agents all           分发 agents 配置到所有平台渠道
# just agents <SLUG>        仅分发到指定渠道（如 claude / codex）
[group('agents')]
agents *ARGS:
    #!/bin/bash
    uv run agents.py agents {{ARGS}}
