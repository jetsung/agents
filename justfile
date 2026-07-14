# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just install / just setup / just setup-dir

set shell := ["python3", "-c"]

# ==================== 安装 (install) ====================

# 安装工具（必带参数）:
#   just install --rec / -r      安装 config.yaml 中 recommended 的推荐 skills
#   just install --all  / -a      安装全部 tools
#   just install <TOOLS_ID>       仅安装指定 id 的 tool
#   just install                  显示用法说明（不安装）
[group('install')]
install ARGS='':
    #!/bin/bash
    python3 agents.py install {{ARGS}}

# 安装 config.yaml 中的推荐 skills: just init
[group('install')]
init:
    #!/bin/bash
    python3 agents.py recommended

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
