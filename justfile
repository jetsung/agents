# AI Agents 配置安装工具
# 使用方法: just <command> [args]
# 示例: just install / just setup / just setup-dir

set shell := ["python3", "-c"]

# 安装 skills: just install / just install weiyun
install SKILL='':
    #!/bin/bash
    if [ -z "{{SKILL}}" ]; then
        python3 install.py install
    else
        python3 install.py install {{SKILL}}
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
