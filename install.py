#!/usr/bin/env python3
import yaml
import subprocess
import os
import sys
import argparse
from pathlib import Path


def load_skills_yaml(project_dir: Path) -> dict:
    yaml_path = project_dir / "skills.yaml"
    if not yaml_path.exists():
        print(f"错误: {yaml_path} 不存在")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def export_env(env_vars: dict):
    for key, value in env_vars.items():
        os.environ[key] = str(value)


def execute_run(run_cmd: str, tmp_dir: Path):
    tmp_dir.mkdir(parents=True, exist_ok=True)
    original_dir = os.getcwd()

    try:
        os.chdir(tmp_dir)
        result = subprocess.run(
            run_cmd,
            shell=True,
            executable=os.environ.get("SHELL", "/bin/sh"),
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            print(f"命令执行失败: {run_cmd}")
            sys.exit(1)
    finally:
        os.chdir(original_dir)


def install_skills(project_dir: Path, skill_filter: str = None):
    data = load_skills_yaml(project_dir)

    global_env = data.get("env") or {}
    if global_env:
        export_env(global_env)

    tools = data.get("tools", [])
    if not tools:
        print("错误: skills.yaml 中缺少 tools 配置")
        sys.exit(1)

    if skill_filter:
        tools = [t for t in tools if t.get("id") == skill_filter]
        if not tools:
            print(f"错误: 未找到 id 为 '{skill_filter}' 的工具")
            sys.exit(1)

    tmp_dir = project_dir / ".tmp"

    for tool in tools:
        tool_id = tool.get("id")
        if not tool_id:
            print("错误: 工具缺少 id 字段")
            sys.exit(1)

        tool_name = tool.get("name", tool_id)
        tool_env = tool.get("env") or {}
        run_cmd = tool.get("run")

        if not run_cmd:
            print(f"错误: 工具 {tool_id} 缺少 run 字段")
            sys.exit(1)

        print(f"安装工具: {tool_name}")

        export_env(tool_env)
        execute_run(run_cmd, tmp_dir)

        print(f'Skills "{tool_name}" 安装完成')
        print()

    suffix = f" (过滤: {skill_filter})" if skill_filter else ""
    print(f"skills 安装完成{suffix}")
    print()


def main():
    parser = argparse.ArgumentParser(description="安装 skills 配置")
    parser.add_argument(
        "-a",
        "--action",
        default="skills",
        help="执行的动作 (默认: skills)",
    )
    parser.add_argument(
        "skill",
        nargs="?",
        help="指定要安装的 skill id（可选）",
    )
    args = parser.parse_args()

    project_dir = Path(__file__).parent.resolve()

    if args.action == "skills":
        install_skills(project_dir, args.skill)
    else:
        print(f"错误: 不支持的动作 '{args.action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
