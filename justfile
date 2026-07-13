# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just install / just setup / just setup-dir

set shell := ["python3", "-c"]

# 安装 tools（工具）: just install / just install weiyun
install TOOL='':
    #!/bin/bash
    if [ -z "{{TOOL}}" ]; then
        python3 install.py install
    else
        python3 install.py install {{TOOL}}
    fi

# 将当前目录链接至 ~/.agents
setup-dir:
    #!/bin/bash
    python3 install.py setup-dir

# 安装 skills 目录到各 AI 工具
setup-skills:
    #!/bin/bash
    python3 install.py setup-skills

# 安装 agents 配置文件到各 AI 工具
setup-agents:
    #!/bin/bash
    python3 install.py setup-agents

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
            python3 install.py setup
            ;;
        *)
            echo "不支持的 target: {{TARGET}}"
            echo "可用: skills, agents, dir"
            exit 1
            ;;
    esac

# ==================== Skills 管理 ====================
# 所有逻辑在 install.py 中实现

# 列出 config.yaml 中配置的 skills 源
skill-list:
    #!/bin/bash
    python3 install.py skills-list

# 列出 config.yaml 中配置的 prompts 源
prompt-list:
    #!/bin/bash
    python3 install.py prompts-list

# 显示当前所有 skills 渠道的 skill 列表
skill-show CHANNEL='':
    #!/bin/bash
    python3 install.py skills-show "{{CHANNEL}}"

# 列出已安装的 skills
skill-installed:
    #!/bin/bash
    python3 install.py skills-installed

# 添加 skill: just skill-add <channel_name> <skill_name>
# 例如: just skill-add antfu vue
skill-add CHANNEL='' SKILL='':
    #!/bin/bash
    if [ -z "{{CHANNEL}}" ] || [ -z "{{SKILL}}" ]; then
        echo "用法: just skill-add <channel_name> <skill_name>"
        echo "例如: just skill-add antfu vue"
        exit 1
    fi
    python3 install.py skills-add "{{CHANNEL}}" "{{SKILL}}"

# 搜索 skills
skill-find QUERY='':
    #!/bin/bash
    if [ -z "{{QUERY}}" ]; then
        python3 install.py skills-find
    else
        python3 install.py skills-find "{{QUERY}}"
    fi
