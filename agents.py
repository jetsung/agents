#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["PyYAML"]
# ///
"""AI Agents 配置安装工具 - 跨平台统一脚本

功能：
- install: 根据 config.yaml 安装工具
- setup-agents: 安装 agents 配置文件到各 AI 工具
- setup: 执行以上所有步骤
"""

import json
import yaml
import subprocess
import os
import sys
import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime

# ==================== 工具函数 ====================


def expand_path(path: str) -> Path:
    """展开路径中的 ~ 和环境变量"""
    return Path(os.path.expanduser(path))


def expand_platform_path(path: str, project_dir: Path = None) -> Path:
    """展开平台配置目录路径

    config.yaml / xskill settings.json 中 path 的取值规则：
    - ~ 开头或绝对路径：原样展开，如 ~/.claude、~/.pi/agent
    - ./ 开头：相对于项目目录（脚本所在仓库），如 ./.pi
    - 其余相对路径（如 .claude）：统一视为位于用户主目录下
    """
    if not path:
        return Path()
    if path.startswith("~") or Path(path).is_absolute():
        return expand_path(path)
    if path == "." or path.startswith(("./", "../")):
        base = project_dir or Path(__file__).parent.resolve()
        return (base / path).resolve()
    return expand_path(f"~/{path}")


def backup_path(path: Path) -> Path:
    """生成备份路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path.parent / f"{path.name}_backup_{timestamp}"


def resolve_env_vars(text: str, env_vars: dict) -> str:
    """解析字符串中的环境变量 $VAR"""
    import re

    def replace_var(match):
        var_name = match.group(1)
        return env_vars.get(var_name, match.group(0))

    return re.sub(r"\$([A-Z_][A-Z0-9_]*)", replace_var, text)


def create_link(target: Path, link_name: Path) -> bool:
    """创建符号链接，支持跨平台

    Args:
        target: 链接目标（必须是绝对路径）
        link_name: 链接名称（必须是绝对路径）

    Returns:
        True 表示成功或跳过，False 表示失败
    """
    # 检查父目录是否存在
    if not link_name.parent.exists():
        print(f"[跳过] 父目录不存在: {link_name.parent}")
        return False

    # 确保 target 是绝对路径
    target = target.resolve()

    # 检查是否已存在
    if link_name.exists() or link_name.is_symlink():
        if link_name.is_symlink():
            # 已是符号链接，检查是否指向正确位置
            current_target = link_name.resolve()
            if current_target == target:
                print(f"[跳过] {link_name} 已经是正确的符号链接。")
                return True
            else:
                print(f"[更新] 更新符号链接: {link_name} -> {target}")
                link_name.unlink()
        elif link_name.is_dir():
            # 是真实目录，进行备份
            backup = backup_path(link_name)
            print(f"[备份] 发现现有目录，正在备份至: {backup}")
            shutil.move(str(link_name), str(backup))
        else:
            # 是真实文件，进行备份
            backup = backup_path(link_name)
            print(f"[备份] 发现现有文件，正在备份至: {backup}")
            shutil.move(str(link_name), str(backup))

    # 创建符号链接
    try:
        if sys.platform == "win32":
            # Windows: 尝试创建 junction（不需要管理员权限）
            if target.is_dir():
                result = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(link_name), str(target)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ["cmd", "/c", "mklink", "/D", str(link_name), str(target)],
                        capture_output=True,
                        text=True,
                    )
            else:
                result = subprocess.run(
                    ["cmd", "/c", "mklink", str(link_name), str(target)],
                    capture_output=True,
                    text=True,
                )
            if result.returncode != 0:
                print(f"[失败] 无法链接: {link_name} (可能需要管理员权限)")
                return False
        else:
            # Unix: 使用 os.symlink
            os.symlink(str(target), str(link_name))

        print(f"[成功] 已链接: {link_name} -> {target}")
        return True
    except OSError as e:
        print(f"[失败] 无法链接: {link_name} ({e})")
        return False


def load_config(project_dir: Path) -> dict:
    """加载 config.yaml 配置"""
    yaml_path = project_dir / "config.yaml"
    if not yaml_path.exists():
        print(f"错误: {yaml_path} 不存在")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ==================== 内置渠道配置 ====================

# 已确认的渠道（config.yaml 与 ~/.xskill/settings.json 中的全部渠道）写死于此，
# 无需在 config.yaml 重复配置即可安装；config.yaml 仍可覆盖同名渠道，
# ~/.xskill/settings.json 仍可补充新渠道。
# 合并优先级：config.yaml 显式配置 > 内置渠道 > ~/.xskill/settings.json 补充。
#
# 说明：
# - 同名渠道同时存在于 config.yaml 与 xskill 时，以 config.yaml 值为准。
# - path 统一为 ~/.xxx 形式；agents 为相对 path 的 agents 配置文件名。
# - langcli 的 agents 为空（与 config.yaml 一致），setup-agents 时跳过。
# - pi（https://github.com/earendil-works/pi-coding-agent）
#   上下文文件（全局）：~/.pi/agent/AGENTS.md
BUILTIN_PLATFORMS = {
    # —— 仓库 config.yaml platforms 段（kilo 在 config.yaml 中处于注释状态，不启用）——
    "claude": {"path": "~/.claude", "agents": "CLAUDE.md"},
    "openclaude": {"path": "~/.openclaude", "agents": "CLAUDE.md"},
    "opencode": {"path": "~/.opencode", "agents": "AGENTS.md"},
    "codex": {"path": "~/.codex", "agents": "AGENTS.md"},
    "qwen": {"path": "~/.qwen", "agents": "AGENTS.md"},
    "codebuddy": {"path": "~/.codebuddy", "agents": "CODEBUDDY.md"},
    "cline": {"path": "~/.cline", "agents": "CLAUDE.md"},
    "factory": {"path": "~/.factory", "agents": "AGENTS.md"},
    "qoder": {"path": "~/.qoder", "agents": "AGENTS.md"},
    "langcli": {"path": "~/.langcli", "agents": ""},
    "gemini": {"path": "~/.gemini", "agents": "GEMINI.md"},
    "atomcode": {"path": "~/.atomcode", "agents": "ATOMCODE.md"},
    # —— ~/.xskill/settings.json platforms 中仅存在于该处的渠道 ——
    "openinterpreter": {"path": "~/.openinterpreter", "agents": "AGENTS.md"},
    "zcode": {"path": "~/.zcode", "agents": "AGENTS.md"},
    "jcode": {"path": "~/.jcode", "agents": "AGENTS.md"},
    "kilo": {"path": "~/.kilocode", "agents": "AGENTS.md"},
    # —— 内置补充：pi ——
    "pi": {
        "path": "~/.pi/agent",
        "agents": "AGENTS.md",
        "ensure_dir": True,
    },
}


def load_platforms(project_dir: Path) -> dict:
    """合并 platforms 配置，优先级由高到低：

    1. 仓库 config.yaml 的 platforms（用户自定义，可覆盖内置同名渠道）
    2. BUILTIN_PLATFORMS 内置渠道（写死，已覆盖 config.yaml 与
       ~/.xskill/settings.json 的完整渠道清单）
    3. ~/.xskill/settings.json 的 platforms（仅补充前两者未出现的渠道）

    每个渠道附带 `_source` 字段标记来源（内置 / config.yaml / xskill），
    供 platforms-list 命令展示，不影响安装逻辑。
    """
    platforms = {}

    # 2. 内置渠道（写死，默认为 base）
    for name, platform in BUILTIN_PLATFORMS.items():
        platforms[name] = {**dict(platform), "_source": "内置"}

    # 1. config.yaml 显式配置（可覆盖内置同名渠道）
    for name, platform in (load_config(project_dir).get("platforms", {}) or {}).items():
        platforms[name] = {**dict(platform or {}), "_source": "config.yaml"}

    # 3. ~/.xskill/settings.json 补充（仅前两者未出现的渠道）
    xskill_path = expand_path("~/.xskill/settings.json")
    if not xskill_path.exists():
        return platforms

    try:
        with open(xskill_path, "r", encoding="utf-8") as f:
            xskill = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[警告] 读取 {xskill_path} 失败: {e}，跳过 xskill 补充")
        return platforms

    xskill_platforms = xskill.get("platforms", {})
    if not xskill_platforms:
        print(f"[警告] {xskill_path} 中未配置 platforms，跳过 xskill 补充")
        return platforms

    for name, platform in xskill_platforms.items():
        if name not in platforms:
            platforms[name] = {**dict(platform or {}), "_source": "xskill"}
    return platforms


# ==================== 安装功能 ====================


def create_agents_dir_link() -> None:
    """将当前目录链接至 ~/.agents"""
    project_dir = Path(__file__).parent.resolve()
    agents_dir = expand_path("~/.agents").resolve()

    print(f"当前项目路径: {project_dir}")
    print(f"Agents 目录: {agents_dir}")
    print("开始建立软链接...")

    if project_dir == agents_dir:
        print("[信息] 当前目录已在 ~/.agents，跳过链接创建。")
        return

    if agents_dir.exists() or agents_dir.is_symlink():
        if agents_dir.is_symlink():
            current_target = agents_dir.resolve()
            if current_target == project_dir:
                print("[跳过] ~/.agents 已正确链接到当前目录。")
                return
            else:
                print(f"[更新] 更新 ~/.agents 链接: {agents_dir} -> {project_dir}")
                agents_dir.unlink()
        else:
            backup = backup_path(agents_dir)
            print(f"[备份] 发现现有目录，正在备份至: {backup}")
            shutil.move(str(agents_dir), str(backup))

    create_link(project_dir, agents_dir)
    print("完成！")


def setup_agents_config() -> None:
    """安装 agents 配置文件到各 AI 工具"""
    project_dir = Path(__file__).parent.resolve()
    agents_dir = expand_path("~/.agents").resolve()

    # 检查 ~/.agents 是否存在
    if not agents_dir.exists():
        print("[信息] ~/.agents 不存在，正在自动创建...")
        create_agents_dir_link()

    # 合并平台配置：config.yaml > 内置渠道 > ~/.xskill/settings.json 补充
    platforms = load_platforms(project_dir)

    print("以 ~/.agents 为基准安装 agents 配置文件...")
    print("开始建立软链接...")

    for name, platform in platforms.items():
        agents_file = platform.get("agents")
        if not agents_file:
            continue

        platform_path = expand_platform_path(platform.get("path", ""), project_dir)
        target = platform_path / agents_file

        # ensure_dir: 目标目录不存在时自动创建（默认跳过，保留原行为）
        if platform.get("ensure_dir") and not platform_path.exists():
            platform_path.mkdir(parents=True, exist_ok=True)
            print(f"[创建] 目录: {platform_path}")

        # 默认源文件为 AGENTS.md
        source = platform.get("source", "AGENTS.md")
        src_path = agents_dir / source

        # 检查源文件是否存在
        if not src_path.exists():
            print(f"[跳过] 源文件不存在: {src_path}")
            continue

        create_link(src_path, target)

    print("完成！")


# ==================== 工具安装功能 ====================


def export_env(env_vars: dict):
    """导出环境变量"""
    for key, value in env_vars.items():
        os.environ[key] = str(value)


def download_file(url: str, dest: Path) -> None:
    """下载文件（跨平台）"""
    print(f"  下载: {url}")
    urllib.request.urlretrieve(url, str(dest))
    print(f"  保存: {dest}")


def unzip_file(src: Path, dest: Path) -> None:
    """解压 zip 文件（跨平台）"""
    print(f"  解压: {src}")
    with zipfile.ZipFile(str(src), "r") as zip_ref:
        zip_ref.extractall(str(dest))
    print(f"  目标: {dest}")


def execute_steps(steps: list, env_vars: dict, project_dir: Path) -> None:
    """执行安装步骤（支持跨平台命令）

    Args:
        steps: 步骤列表
        env_vars: 环境变量
        project_dir: 项目根目录
    """
    tmp_dir = project_dir / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for step in steps:
        if isinstance(step, str):
            # 旧格式：shell 命令字符串
            resolved = resolve_env_vars(step, env_vars)
            result = subprocess.run(
                resolved,
                shell=True,
                cwd=str(tmp_dir),
                capture_output=False,
                text=True,
            )
            if result.returncode != 0:
                print(f"命令执行失败: {resolved}")
                sys.exit(1)
        elif isinstance(step, dict):
            # 新格式：字典命令
            # dest 相对于项目根目录，src 相对于临时目录
            if "download" in step:
                url = resolve_env_vars(step["download"], env_vars)
                dest = tmp_dir / step.get("dest", url.split("/")[-1])
                download_file(url, dest)

                # extract 未设置或为 true 时，默认解压到 skills/
                # extract 为 false 时，不解压
                # extract 为路径字符串时，解压到指定路径
                extract_to = step.get("extract", True)
                if extract_to is not False:
                    if extract_to is True:
                        extract_to = "skills"
                    if not os.path.isabs(extract_to) and not extract_to.startswith("~"):
                        extract_path = project_dir / extract_to
                    else:
                        extract_path = expand_path(extract_to)
                    extract_path.mkdir(parents=True, exist_ok=True)
                    unzip_file(dest, extract_path)
            elif "unzip" in step:
                src = tmp_dir / resolve_env_vars(step["unzip"], env_vars)
                # 默认解压到 skills 目录
                dest_str = step.get("dest", "skills")
                if not os.path.isabs(dest_str) and not dest_str.startswith("~"):
                    dest = project_dir / dest_str
                else:
                    dest = expand_path(dest_str)
                dest.mkdir(parents=True, exist_ok=True)
                unzip_file(src, dest)
            elif "copy" in step:
                src = tmp_dir / resolve_env_vars(step["copy"], env_vars)
                dest_str = step.get("dest", ".")
                if not os.path.isabs(dest_str) and not dest_str.startswith("~"):
                    dest = project_dir / dest_str
                else:
                    dest = expand_path(dest_str)
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copytree(str(src), str(dest), dirs_exist_ok=True)
            elif "move" in step:
                src = tmp_dir / resolve_env_vars(step["move"], env_vars)
                dest_str = step.get("dest", ".")
                if not os.path.isabs(dest_str) and not dest_str.startswith("~"):
                    dest = project_dir / dest_str
                else:
                    dest = expand_path(dest_str)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
            elif "mkdir" in step:
                d = project_dir / resolve_env_vars(step["mkdir"], env_vars)
                d.mkdir(parents=True, exist_ok=True)
            elif "remove" in step:
                target_str = resolve_env_vars(step["remove"], env_vars)
                if not os.path.isabs(target_str) and not target_str.startswith("~"):
                    target = project_dir / target_str
                else:
                    target = expand_path(target_str)
                if target.is_file():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(str(target))
            elif "run" in step:
                run_cmd = resolve_env_vars(step["run"], env_vars)
                result = subprocess.run(
                    run_cmd,
                    shell=True,
                    cwd=str(tmp_dir),
                    capture_output=False,
                    text=True,
                )
                if result.returncode != 0:
                    print(f"命令执行失败: {run_cmd}")
                    sys.exit(1)
            else:
                print(f"未知命令: {step}")
                sys.exit(1)
        else:
            print(f"无效的步骤格式: {step}")
            sys.exit(1)


def install_tools(project_dir: Path, tool_filter: str = None):
    """根据 config.yaml 安装工具"""
    config = load_config(project_dir)

    global_env = config.get("env") or {}
    if global_env:
        export_env(global_env)

    tools = config.get("tools", [])
    if not tools:
        print("错误: config.yaml 中缺少 tools 配置")
        sys.exit(1)

    if tool_filter:
        tools = [t for t in tools if t.get("id") == tool_filter]
        if not tools:
            print(f"错误: 未找到 id 为 '{tool_filter}' 的工具")
            sys.exit(1)

    has_skill = False
    has_tool = False
    for tool in tools:
        tool_id = tool.get("id")
        if not tool_id:
            print("错误: 工具缺少 id 字段")
            sys.exit(1)

        tool_name = tool.get("name", tool_id)
        tool_type = tool.get("type", "tool")
        tool_env = tool.get("env") or {}
        steps = tool.get("steps")
        run_cmd = tool.get("run")

        if tool_type == "skill":
            has_skill = True
        else:
            has_tool = True

        # 合并环境变量
        merged_env = {**global_env, **tool_env}
        export_env(merged_env)

        print(f"安装工具: {tool_name}")

        if steps:
            # 新格式：steps 列表
            execute_steps(steps, merged_env, project_dir)
        elif run_cmd:
            # 兼容旧格式：run 字符串
            execute_steps([run_cmd], merged_env, project_dir)
        else:
            print(f"错误: 工具 {tool_id} 缺少 steps 或 run 字段")
            sys.exit(1)

        if tool_type == "skill":
            print(f'Skills "{tool_name}" 安装完成')
        else:
            print(f'Tool "{tool_name}" 安装完成')
        print()
        print("-" * 80)

    suffix = f" (过滤: {tool_filter})" if tool_filter else ""
    if has_skill and not has_tool:
        print(f"skills 安装完成{suffix}")
    elif has_tool and not has_skill:
        print(f"工具安装完成{suffix}")
    else:
        print(f"工具安装完成（含 skills）{suffix}")
    print()


# ==================== 主函数 ====================


def cmd_tools_list(project_dir: Path, tool_id: str = None) -> None:
    """列出 config.yaml 中配置的 tools

    Args:
        tool_id: 可选工具 id，传入时仅显示该工具信息。
    """
    config = load_config(project_dir)
    tools = config.get("tools", [])

    if not tools:
        print("没有配置 tools")
        return

    if tool_id:
        tools = [t for t in tools if t.get("id") == tool_id]
        if not tools:
            print(f"错误: 未找到 id 为 '{tool_id}' 的工具")
            sys.exit(1)

    print(f'{"ID":<20} {"名称":<20} 类型')
    print("-" * 80)
    for t in tools:
        print(f'{t.get("id", ""):<20} {t.get("name", ""):<20} {t.get("type", "tool")}')


def cmd_platforms_list(project_dir: Path, name: str = None) -> None:
    """列出所有平台渠道（内置 + config.yaml + xskill 补充）

    Args:
        name: 可选渠道名，传入时仅显示该渠道信息。
    """
    platforms = load_platforms(project_dir)

    if not platforms:
        print("没有可用的平台渠道")
        return

    if name:
        if name not in platforms:
            print(f"错误: 未找到渠道 '{name}'")
            sys.exit(1)
        platforms = {name: platforms[name]}

    use_color = sys.stdout.isatty() and sys.platform != "win32"

    print(f'{"渠道":<16} {"目标路径":<46} {"agents":<12} {"来源":<12} {"存在"}')
    print("-" * 100)
    for pname, platform in platforms.items():
        agents = platform.get("agents") or "-"
        path = str(expand_platform_path(platform.get("path", ""), project_dir))
        src = platform.get("_source", "config.yaml")
        exists = "存在" if Path(path).exists() else "缺失"
        line = f"{pname:<16} {path:<46} {agents:<12} {src:<12} {exists}"
        if exists == "存在" and use_color:
            # 目录存在：整行标黄
            line = f"\033[33m{line}\033[0m"
        print(line)


def main():
    parser = argparse.ArgumentParser(description="AI Agents 配置安装工具")
    subparsers = parser.add_subparsers(dest="action", help="执行的动作")

    # install
    p_install = subparsers.add_parser(
        "install",
        help="安装 tools：--all/-a 全部、或指定 TOOLS ID",
    )
    install_grp = p_install.add_mutually_exclusive_group(required=True)
    install_grp.add_argument("-a", "--all", action="store_true", help="安装 config.yaml 中的全部 tools")
    install_grp.add_argument("tool_id", nargs="?", help="指定要安装的 TOOLS ID")

    # setup-agents
    subparsers.add_parser("setup-agents", help="安装 agents 配置文件到各 AI 工具")

    # setup
    subparsers.add_parser("setup", help="完整初始化（链接 + 安装 agents）")

    # tools-list
    p_tools_list = subparsers.add_parser(
        "tools-list",
        help="列出 config.yaml 中配置的 tools（可选 <id> 指定单个工具）",
    )
    p_tools_list.add_argument("tool_id", nargs="?", default="", help="可选工具 id，缺省列出全部")

    # platforms-list
    p_platforms_list = subparsers.add_parser(
        "platforms-list",
        help="列出所有平台渠道：内置 + config.yaml + xskill 补充（可选 <name> 指定单个）",
    )
    p_platforms_list.add_argument("name", nargs="?", default="", help="可选渠道名，缺省列出全部")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    project_dir = Path(__file__).parent.resolve()

    if args.action == "install":
        if args.all:
            install_tools(project_dir, None)
        else:
            install_tools(project_dir, args.tool_id)
    elif args.action == "setup-agents":
        setup_agents_config()
    elif args.action == "setup":
        create_agents_dir_link()
        setup_agents_config()
        print("")
        print("初始化完成！")
    elif args.action == "tools-list":
        cmd_tools_list(project_dir, args.tool_id or None)
    elif args.action == "platforms-list":
        cmd_platforms_list(project_dir, args.name or None)


if __name__ == "__main__":
    main()
