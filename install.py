#!/usr/bin/env python3
"""AI Agents 配置安装工具 - 跨平台统一脚本

功能：
- install: 根据 config.yaml 安装技能
- setup-dir: 将当前目录链接至 ~/.agents
- setup-skills: 安装 skills 目录到各 AI 工具
- setup-agents: 安装 agents 配置文件到各 AI 工具
- setup: 执行以上所有步骤
"""

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


def setup_skills_dir() -> None:
    """安装 skills 目录到各 AI 工具"""
    project_dir = Path(__file__).parent.resolve()
    agents_dir = expand_path("~/.agents").resolve()

    # 检查 ~/.agents 是否存在
    if not agents_dir.exists():
        print("[信息] ~/.agents 不存在，正在自动创建...")
        create_agents_dir_link()

    # 从配置文件读取平台配置
    config = load_config(project_dir)
    platforms = config.get("platforms", {})

    if not platforms:
        print("[警告] config.yaml 中未配置 platforms")
        return

    skills_source = agents_dir / "skills"
    print("以 ~/.agents 为基准安装 skills...")
    print("开始建立软链接...")

    for name, platform in platforms.items():
        skills_dir = platform.get("skills")
        if not skills_dir:
            continue

        platform_path = expand_path(platform.get("path", ""))
        target = platform_path / skills_dir
        create_link(skills_source, target)

    print("完成！")


def setup_agents_config() -> None:
    """安装 agents 配置文件到各 AI 工具"""
    project_dir = Path(__file__).parent.resolve()
    agents_dir = expand_path("~/.agents").resolve()

    # 检查 ~/.agents 是否存在
    if not agents_dir.exists():
        print("[信息] ~/.agents 不存在，正在自动创建...")
        create_agents_dir_link()

    # 从配置文件读取平台配置
    config = load_config(project_dir)
    platforms = config.get("platforms", {})

    if not platforms:
        print("[警告] config.yaml 中未配置 platforms")
        return

    print("以 ~/.agents 为基准安装 agents 配置文件...")
    print("开始建立软链接...")

    for name, platform in platforms.items():
        agents_file = platform.get("agents")
        if not agents_file:
            continue

        platform_path = expand_path(platform.get("path", ""))
        target = platform_path / agents_file

        # 默认源文件为 AGENTS.md
        source = platform.get("source", "AGENTS.md")
        src_path = agents_dir / source

        # 检查源文件是否存在
        if not src_path.exists():
            print(f"[跳过] 源文件不存在: {src_path}")
            continue

        create_link(src_path, target)

    print("完成！")


# ==================== Skills 安装功能 ====================


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
            else:
                print(f"未知命令: {step}")
                sys.exit(1)
        else:
            print(f"无效的步骤格式: {step}")
            sys.exit(1)


def install_skills(project_dir: Path, skill_filter: str = None):
    """根据 config.yaml 安装技能"""
    config = load_config(project_dir)

    global_env = config.get("env") or {}
    if global_env:
        export_env(global_env)

    tools = config.get("tools", [])
    if not tools:
        print("错误: config.yaml 中缺少 tools 配置")
        sys.exit(1)

    if skill_filter:
        tools = [t for t in tools if t.get("id") == skill_filter]
        if not tools:
            print(f"错误: 未找到 id 为 '{skill_filter}' 的工具")
            sys.exit(1)

    for tool in tools:
        tool_id = tool.get("id")
        if not tool_id:
            print("错误: 工具缺少 id 字段")
            sys.exit(1)

        tool_name = tool.get("name", tool_id)
        tool_env = tool.get("env") or {}
        steps = tool.get("steps")
        run_cmd = tool.get("run")

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

        print(f'Skills "{tool_name}" 安装完成')
        print()

    suffix = f" (过滤: {skill_filter})" if skill_filter else ""
    print(f"skills 安装完成{suffix}")
    print()


# ==================== 主函数 ====================


def main():
    parser = argparse.ArgumentParser(description="AI Agents 配置安装工具")
    parser.add_argument(
        "action",
        choices=["install", "setup-dir", "setup-skills", "setup-agents", "setup"],
        help="执行的动作",
    )
    parser.add_argument(
        "skill",
        nargs="?",
        help="指定要安装的 skill id（仅 install 动作有效）",
    )

    args = parser.parse_args()
    project_dir = Path(__file__).parent.resolve()

    if args.action == "install":
        install_skills(project_dir, args.skill)
    elif args.action == "setup-dir":
        create_agents_dir_link()
    elif args.action == "setup-skills":
        setup_skills_dir()
    elif args.action == "setup-agents":
        setup_agents_config()
    elif args.action == "setup":
        create_agents_dir_link()
        setup_skills_dir()
        setup_agents_config()
        print("")
        print("初始化完成！")


if __name__ == "__main__":
    main()
