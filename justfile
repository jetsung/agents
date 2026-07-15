# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just tools install / just skill-rec install / just setup / just setup-dir

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

# ==================== 推荐 skills 安装 (skill-rec) ====================

# just skill-rec install --all / -a   安装全部推荐来源下的 skills
# just skill-rec install <SOURCE>     仅安装指定推荐来源（name/url）下的 skills
# just skill-rec list  --all / -a     列出全部推荐来源
# just skill-rec list  <SOURCE>       仅列出指定来源下的 skills
[group('skills')]
skill-rec *ARGS:
    #!/bin/bash
    set -- {{ARGS}}
    sub="${1:-}"; shift || true
    case "$sub" in
        install)
            # 必须带参数：--all/-a 安装全部；来源名/skill 名安装指定
            if [ -z "$*" ]; then
                echo "用法: just skill-rec install [--all|-a|<SOURCE>|<SKILL>]"
                exit 1
            fi
            if [[ "$*" == *"--all"* ]] || [[ "$*" == *"-a"* ]]; then
                python3 agents.py recommended
            else
                python3 agents.py recommended "$*"
            fi
            ;;
        list)
            # 无参列出全部；否则列出指定来源
            if [ -z "$*" ]; then
                python3 agents.py recommended-list
            else
                python3 agents.py recommended-list "$*"
            fi
            ;;
        *)
            echo "用法: just skill-rec <install|list> [--all|-a|<SOURCE>|<SKILL>]"
            exit 1
            ;;
    esac

# ==================== 初始化 (setup) ====================

# 将当前目录链接至 ~/.agents
[group('setup')]
setup-dir:
    #!/bin/bash
    python3 agents.py setup-dir

# 安装 skills 目录到各 AI 工具
[group('setup')]
setup-skills:
    #!/bin/bash
    python3 agents.py setup-skills

# 安装 agents 配置文件到各 AI 工具
[group('setup')]
setup-agents:
    #!/bin/bash
    python3 agents.py setup-agents

# 完整初始化（链接 + 安装 skills + 安装 agents）
# 支持: just setup / just setup skills / just setup agents / just setup dir
[group('setup')]
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
            python3 agents.py setup
            ;;
        *)
            echo "不支持的 target: {{TARGET}}"
            echo "可用: skills, agents, dir"
            exit 1
            ;;
    esac

# ==================== 列表 (list) ====================

# 统一列表入口: just list <skills|prompts|skill|tools>
[group('list')]
list KIND='':
    #!/bin/bash
    python3 agents.py list "{{KIND}}"

# ==================== Skills 管理 (skills) ====================

# 列出 config.yaml 中配置的 skills 源
[group('skills')]
skill-list:
    #!/bin/bash
    python3 agents.py skills-list

# 列出 config.yaml 中配置的 prompts 源
[group('prompts')]
prompt-list:
    #!/bin/bash
    python3 agents.py prompts-list

# 显示 skills 渠道的 skill 列表（--all/-a 全部渠道，<channel> 指定渠道）
[group('skills')]
skill-show ARGS='':
    #!/bin/bash
    python3 agents.py skills-show {{ARGS}}

# 按名称查询单个 skill 的元信息
#   just skill-query <skill>            跨所有 config 渠道查找
#   just skill-query <skill> <CHANNEL>  指定渠道（config name / ORG/REPO / URL）
[group('skills')]
skill-query SKILL CHANNEL='':
    #!/bin/bash
    if [ -z "{{SKILL}}" ]; then
        echo "用法: just skill-query <skill> [<CHANNEL>]"
        echo "  <skill>    必填，要查询的 skill 名称"
        echo "  <CHANNEL>  可选，指定渠道（config name / ORG/REPO / URL）；留空则跨所有渠道"
        exit 1
    fi
    python3 agents.py skills-query "{{SKILL}}" {{CHANNEL}}

# 列出已安装的 skills（--all/-a 额外显示 name/description/version）
[group('skills')]
skill-installed ARGS='':
    #!/bin/bash
    python3 agents.py skills-installed {{ARGS}}

# 添加 skill: just skill-add <channel_name> <skill_name>
# 例如: just skill-add antfu vue
[group('skills')]
skill-add CHANNEL='' SKILL='':
    #!/bin/bash
    if [ -z "{{CHANNEL}}" ] || [ -z "{{SKILL}}" ]; then
        echo "用法: just skill-add <channel_name> <skill_name>"
        echo "例如: just skill-add antfu vue"
        exit 1
    fi
    python3 agents.py skills-add "{{CHANNEL}}" "{{SKILL}}"

# 移除已安装 skill: just skill-remove -a (全部) / just skill-remove <SKILL_PATH>
[group('skills')]
skill-remove ARGS='':
    #!/bin/bash
    python3 agents.py skills-remove {{ARGS}}

# 搜索 skills
[group('skills')]
skill-find QUERY='':
    #!/bin/bash
    if [ -z "{{QUERY}}" ]; then
        python3 agents.py skills-find
    else
        python3 agents.py skills-find "{{QUERY}}"
    fi
