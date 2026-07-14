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
import re
import argparse
import shutil
import tempfile
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

    suffix = f" (过滤: {skill_filter})" if skill_filter else ""
    if has_skill and not has_tool:
        print(f"skills 安装完成{suffix}")
    elif has_tool and not has_skill:
        print(f"工具安装完成{suffix}")
    else:
        print(f"工具安装完成（含 skills）{suffix}")
    print()


# ==================== 主函数 ====================


def cmd_skills_list(project_dir: Path) -> None:
    """列出 config.yaml 中配置的 skills 源"""
    config = load_config(project_dir)
    skills = config.get("skills", [])

    if not skills:
        print("没有配置 skills")
        return

    print(f'{"名称":<20} {"URL":<45} depth')
    print("-" * 80)
    for s in skills:
        print(f'{s["name"]:<20} {s["url"]:<45} {s.get("depth", 1)}')


def cmd_prompts_list(project_dir: Path) -> None:
    """列出 config.yaml 中配置的 prompts 源"""
    config = load_config(project_dir)
    prompts = config.get("prompts", [])

    if not prompts:
        print("没有配置 prompts")
        return

    print(f'{"名称":<20} URL')
    print("-" * 80)
    for p in prompts:
        print(f'{p["name"]:<20} {p["url"]}')


def resolve_source(channel: str) -> str:
    """判断 channel 是否为 user/repo 格式或 URL，返回可直接用于 npx skills add 的源

    支持格式:
    - user/repo (GitHub 等)
    - https://github.com/user/repo
    - https://gitlab.com/user/repo
    - https://example.com/user/repo (自建)
    - git@github.com:user/repo.git (SSH)
    """
    # URL with scheme (https://, http://, git://, ssh://)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', channel):
        return channel
    # SSH format
    if channel.startswith('git@') or channel.startswith('ssh@'):
        return channel
    # Looks like user/repo (contains /, no spaces, doesn't start with / or .)
    if '/' in channel and ' ' not in channel and not channel.startswith('/') and not channel.startswith('.'):
        return channel
    return ""


def list_skills_from_repo(source: str, depth: int = 1) -> list:
    """自管 git clone 某仓库并列出其 skills/ 目录下的可用 skill 及元信息

    流程：mktemp 缓存 → clone（quiet）→ sparse-checkout skills/ →
    动态分支 checkout → 按 `depth` 递归到真实 skill 目录 → 返回每个 skill 的
    {name, description, version} → 清理临时目录。
    失败或无 skills/ 目录时返回 [] 并打印提示。

    Args:
        source: 仓库来源（URL / ORG-REPO / config name 由调用方解析后的 url）
        depth: skill 相对 `skills/` 的嵌套层级（默认 1，即 skills/<skill>；
               2 表示 skills/<category>/<skill>）。下钻 depth-1 次定位真实 skill。

    Returns:
        list[dict]: 每个元素 {"name": 目录名, "description": str, "version": str,
                      "path": 相对 skills/ 的路径（单层为 <skill>，两层为 <cat>/<skill>）}
    """
    try:
        url = normalize_git_url(source)
    except ValueError as e:
        print(f"错误: {e}")
        return []

    if shutil.which("git") is None:
        print("错误: 未找到 git 命令，请先安装 git")
        return []

    quiet = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp = Path(tempfile.mkdtemp(prefix="agents-skills-"))
    try:
        result = subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1", url, "."],
            cwd=str(tmp), **quiet,
        )
        if result.returncode != 0:
            print(f"错误: git clone 失败 ({url})")
            return []

        subprocess.run(["git", "-C", str(tmp), "sparse-checkout", "init", "--cone"], **quiet)
        subprocess.run(["git", "-C", str(tmp), "sparse-checkout", "set", "skills"], **quiet)

        branch = get_default_branch(tmp)
        subprocess.run(["git", "-C", str(tmp), "checkout", branch], **quiet)

        skills_path = tmp / "skills"
        if not skills_path.is_dir():
            print(f"提示: 仓库 {url} 中不存在 skills/ 目录")
            return []

        # 按 depth 逐级下钻 depth-1 次，定位真实 skill 目录集合。
        # depth=1 → skills/ 的直接子目录；depth=2 → skills/<cat>/<skill>。
        level = sorted(p for p in skills_path.iterdir() if p.is_dir())
        for _ in range(max(0, depth - 1)):
            level = sorted(
                c for p in level for c in p.iterdir() if c.is_dir()
            )

        result = []
        for d in level:
            # 仅含 SKILL.md 的末层目录才算有效 skill，跳过空目录/分类节点
            if not (d / "SKILL.md").is_file():
                continue
            info = parse_skill_md(d / "SKILL.md")
            result.append({
                "name": info.get("name") or d.name,
                "description": info.get("description") or "无",
                "version": info.get("version") or "无",
                "path": str(d.relative_to(skills_path)),
            })
        return result
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _channel_depth(channel: str, skills: list) -> int:
    """解析某渠道配置的 depth（默认 1）

    - channel 不含 '/' 且在 skills 模块存在同名 name → 取其 depth
    - 否则（ORG/REPO、URL、或未配置）→ 回退 1
    """
    if "/" not in channel:
        for s in skills:
            if s.get("name") == channel:
                return int(s.get("depth", 1) or 1)
    return 1


def resolve_show_source(channel: str, skills: list) -> str:
    """解析 skill-show 的渠道来源

    - channel 不含 '/' 且在 skills 模块存在同名 name → 返回其 url
    - 否则按 normalize_git_url 解析（ORG/REPO → https://github.com/ORG/REPO；url → 原样）
    """
    if "/" not in channel:
        for s in skills:
            if s.get("name") == channel:
                url = s.get("url")
                if not url:
                    print(f"错误: channel '{channel}' 缺少 url 字段")
                    sys.exit(1)
                return url
    return normalize_git_url(channel)


def _print_skill_list(skill_list: list) -> None:
    """格式化打印 list_skills_from_repo 返回的 skill 元信息列表

    风格与 `skill-installed --all` 对齐：每个 skill 以 名称/描述/版本
    分行展示，末尾用 `----` 分隔。嵌套布局（两层及以上）额外展示 路径，
    便于用户按 `<cat>/<skill>` 形式安装。
    """
    if skill_list:
        for skill in skill_list:
            print(f"名称: {skill['name']}")
            # 嵌套 skill 显示相对 skills/ 的真实路径（如 engineering/grill-with-docs）
            spath = skill.get("path", "")
            name = skill.get("name", "")
            if spath and spath != name:
                print(f"路径: {spath}")
            print(f"描述: {skill['description']}")
            print(f"版本: {skill['version']}")
            print("-" * 80)
    else:
        print("  （无可用 skill）")


def query_skill(project_dir: Path, skill: str, channel: str = "") -> None:
    """按名称查询单个 skill 的元信息（自管 git clone 方式）

    两种模式：
      - 指定 channel：用 `resolve_show_source` 解析来源（config name → url、
        ORG/REPO → https://github.com/ORG/REPO、URL → 原样），clone 该渠道
        并在其 skills/ 下过滤匹配 `<skill>` 的项。
      - 不指定 channel：遍历 config.yaml `skills` 模块的全部渠道，逐个 clone
        过滤，收集所有命中项并分组展示。

    匹配规则：与 `list_skills_from_repo` 返回的 `name`（SKILL.md frontmatter）
    或目录名精确相等（大小写敏感）即命中。

    Args:
        skill: 要查询的 skill 名称
        channel: 可选渠道（config name / ORG/REPO / URL）；留空则跨所有渠道
    """
    config = load_config(project_dir)
    skills = config.get("skills", [])

    # 从 list_skills_from_repo 的结果里过滤出匹配 skill 的项
    # name 已优先取 SKILL.md 的 name，回退为目录名，故精确比较 name 即可
    def _match(items: list) -> list:
        return [it for it in items if it["name"] == skill]

    found_any = False

    if channel:
        source = resolve_show_source(channel, skills)
        items = list_skills_from_repo(source, _channel_depth(channel, skills))
        hits = _match(items)
        if hits:
            found_any = True
            _print_skill_list(hits)
    else:
        if not skills:
            print("没有配置 skills")
            return
        for s in skills:
            name = s.get("name", "")
            url = s.get("url")
            if not url:
                continue
            items = list_skills_from_repo(url, s.get("depth", 1))
            hits = _match(items)
            if hits:
                found_any = True
                print(f"\n渠道: {name}")
                _print_skill_list(hits)

    if not found_any:
        scope = f" 渠道 '{channel}' 下" if channel else "所有渠道中"
        print(f"未找到 skill '{skill}'（{scope}）")


def cmd_skills_show(project_dir: Path, channel: str = "", all: bool = False) -> None:
    """显示 skills 渠道中可用的 skill 列表（自管 git clone 方式）

    参数契约（与 install 对齐）：
      - 无参数且无 --all → 显示用法帮助
      - --all / -a → 列出 config.yaml skills 模块所有渠道的 skill
      - <channel> → 解析来源后列出该渠道 skills/ 下的 skill
        · 仅 name（无 /）→ 取 config 中同名渠道的 url
        · ORG/REPO（含 /）→ https://github.com/ORG/REPO
        · url → 原样

    Args:
        channel: 指定渠道（config 中的 name / ORG/REPO / URL）；留空则依赖 all 参数
        all: 为 True 时列出 config.yaml skills 模块所有渠道的 skill
    """
    config = load_config(project_dir)
    skills = config.get("skills", [])

    # 无参数且无 --all → 显示用法帮助
    if not channel and not all:
        print("用法: just skill-show [--all|-a] [<channel>]")
        print("  --all / -a        列出 config.yaml 中所有渠道的 skill")
        print("  <channel>         指定渠道（config name / ORG/REPO / URL）列出其 skill")
        print("  无参数             显示本帮助")
        return

    if all:
        if not skills:
            print("没有配置 skills")
            return
        for s in skills:
            name = s.get("name", "")
            url = s.get("url")
            if not url:
                continue
            print(f"\n{'='*80}")
            print(f"渠道: {name} ({url})")
            print("=" * 80)
            _print_skill_list(list_skills_from_repo(url, s.get("depth", 1)))
        return

    # 指定渠道
    source = resolve_show_source(channel, skills)
    print(f"\n{'='*80}")
    print(f"渠道: {channel} ({source})")
    print("=" * 80)
    _print_skill_list(list_skills_from_repo(source, _channel_depth(channel, skills)))


def cmd_skills_installed(all: bool = False) -> None:
    """列出当前项目目录下已安装的 skills（扫描项目内 skills/ 目录）

    Args:
        all: 为 True 时，额外从每个 skill 的 SKILL.md 读取并展示
             name / description / metadata.version；为 False 时仅列名称与路径。
    """
    project_dir = Path(__file__).parent.resolve()
    skills_dir = project_dir / "skills"

    if not skills_dir.exists():
        print("没有已安装 skills")
        return

    installed = [d.name for d in skills_dir.iterdir() if d.is_dir()]
    if not installed:
        print("没有已安装 skills")
        return

    if not all:
        print(f'{"名称":<30} 路径')
        print("-" * 80)
        for name in installed:
            print(f"{name:<30} {skills_dir / name}")
        return

    # --all：展示每个 skill 的 SKILL.md 元信息
    for name in installed:
        info = parse_skill_md(skills_dir / name / "SKILL.md")
        display_name = info.get("name") or name
        version = info.get("version") or "无"
        description = info.get("description") or "无"
        print(f"名称: {display_name}")
        print(f"路径: {skills_dir / name}")
        print(f"版本: {version}")
        print(f"描述: {description}")
        print("-" * 80)


def _confirm(prompt: str) -> bool:
    """读取用户输入做二次确认，默认否（仅 y/Y 返回 True）"""
    try:
        ans = input(f"{prompt} (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return ans in ("y", "yes")


def cmd_skills_remove(all: bool = False, skill_path: str = "") -> None:
    """移除项目内已安装的 skill

    Args:
        all: 为 True 时删除 skills/ 下的所有子目录（所有 skill）
        skill_path: 指定要删除的 skill 目录名（相对 skills/），如 writing-great-skills
    两者均未提供时由调用方显示用法帮助。
    """
    project_dir = Path(__file__).parent.resolve()
    skills_dir = project_dir / "skills"

    if not skills_dir.exists():
        print("没有已安装 skills")
        return

    if all:
        targets = [d for d in sorted(skills_dir.iterdir()) if d.is_dir()]
        if not targets:
            print("没有已安装 skills")
            return
        print(f"将删除 {len(targets)} 个 skill：")
        for t in targets:
            print(f"  - {t.name}")
        if not _confirm("确认删除全部 skill"):
            print("已取消")
            return
        for t in targets:
            shutil.rmtree(t, ignore_errors=True)
            print(f"已删除: {t.name}")
        return

    # 删除指定单个 skill
    if not skill_path:
        print("用法: python3 agents.py skills-remove [-a | --all | <SKILL_PATH>]")
        print("  -a / --all      删除 skills/ 下的所有 skill")
        print("  <SKILL_PATH>    删除指定 skill（相对 skills/ 的目录名）")
        return

    # 路径安全校验：仅允许 skills/ 内的直接子目录，拒绝越界（如 ../foo）
    target = (skills_dir / skill_path).resolve()
    if target != skills_dir.resolve() and skills_dir.resolve() not in target.parents:
        print(f"错误: 非法路径 '{skill_path}'（不允许越界）")
        sys.exit(1)

    if not target.exists() or not target.is_dir():
        print(f"错误: 未找到 skill '{skill_path}'")
        sys.exit(1)

    print(f"将删除: {target}")
    if not _confirm("确认删除该 skill"):
        print("已取消")
        return
    shutil.rmtree(target, ignore_errors=True)
    print(f"已删除: {skill_path}")


def cmd_skills_find(query: str = "") -> None:
    """搜索 skills"""
    cmd = ["npx", "skills", "find"]
    if query:
        cmd.append(query)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def cmd_tools_list(project_dir: Path) -> None:
    """列出 config.yaml 中配置的 tools"""
    config = load_config(project_dir)
    tools = config.get("tools", [])

    if not tools:
        print("没有配置 tools")
        return

    print(f'{"ID":<20} {"名称":<20} 类型')
    print("-" * 80)
    for t in tools:
        print(f'{t.get("id", ""):<20} {t.get("name", ""):<20} {t.get("type", "tool")}')


def cmd_list(kind: str) -> None:
    """统一列表入口，按 kind 分发到对应列表逻辑

    支撑 `just list <skills|prompts|skill|tools>`。

    Args:
        kind: 列表类型，取值 skills / prompts / skill / tools
    """
    project_dir = Path(__file__).parent.resolve()

    if kind == "skills":
        cmd_skills_list(project_dir)
    elif kind == "prompts":
        cmd_prompts_list(project_dir)
    elif kind == "skill":
        cmd_skills_installed()
    elif kind == "tools":
        cmd_tools_list(project_dir)
    else:
        print("用法: just list <skills|prompts|skill|tools>")
        sys.exit(1)


def normalize_git_url(source: str) -> str:
    """将 source 归一化为完整 git URL

    - ORG/REPO 形式自动补全为 https://github.com/ORG/REPO
    - 已是 URL（http(s)://、git@、ssh:// 等）原样返回
    - 其它形式报错
    """
    source = source.strip()
    # 已是 URL：scheme 形式或 SSH (git@...) 或含 .git
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', source):
        return source
    if source.startswith('git@') or source.startswith('ssh@'):
        return source
    if source.endswith('.git'):
        return source
    # ORG/REPO 形式（含 /、无空格、不以 / 或 . 开头）
    if '/' in source and ' ' not in source and not source.startswith('/') and not source.startswith('.'):
        return f"https://github.com/{source}"
    raise ValueError(f"无法识别的 git 来源: {source}（需为 URL 或 ORG/REPO 形式）")


def get_default_branch(repo_dir: Path) -> str:
    """解析仓库实际默认分支

    优先从 remote HEAD 解析；取不到则回退 main。
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True, text=True,
        )
        if out.returncode == 0:
            # 形如 refs/remotes/origin/<branch>
            ref = out.stdout.strip()
            if "origin/" in ref:
                return ref.split("origin/")[-1]
        # 备选：git remote show origin
        out2 = subprocess.run(
            ["git", "-C", str(repo_dir), "remote", "show", "origin"],
            capture_output=True, text=True,
        )
        if out2.returncode == 0:
            for line in out2.stdout.splitlines():
                line = line.strip()
                if line.startswith("HEAD branch:"):
                    branch = line.split(":", 1)[1].strip()
                    if branch and branch != "(unknown)":
                        return branch
    except Exception:
        pass
    return "main"


def parse_skill_md(skill_md: Path) -> dict:
    """解析 SKILL.md 的 YAML frontmatter，返回 name/description/metadata.version"""
    if not skill_md.exists():
        return {}
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    # 取首个 --- ... --- 之间的 frontmatter
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip("\n")
    try:
        data = yaml.safe_load(fm) or {}
    except yaml.YAMLError:
        return {}
    meta = data.get("metadata") or {}
    return {
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "version": (meta.get("version") if isinstance(meta, dict) else "") or "",
    }


def git_clone_skill(source: str, skill_name: str, dest_name: str = None) -> None:
    """通过 git clone + sparse-checkout 将 skill 拉取到当前项目目录下的 skills/<name>

    流程（对应用户的 agents-skills 脚本）：
      1. 归一化 source 为完整 git URL
      2. mktemp 创建临时缓存目录
      3. git clone --filter=blob:none --no-checkout --depth 1 <url> .
      4. git sparse-checkout init --cone
      5. git sparse-checkout set skills/<skill_name>
      6. 按实际默认分支 git checkout <branch>
      7. 将临时目录中的 skills/<skill_name> 迁移到项目内 skills/<dest_name>
      8. 清理临时目录

    Args:
        source: 仓库来源（完整 git URL）
        skill_name: 仓库内 skills/ 下的相对路径（单层 skills/<skill> 或两层 skills/<cat>/<skill>）
        dest_name: 落在项目内 skills/ 下的目录名；默认同 skill_name 的末级目录名。
                   两层渠道可传 `<cat>_<skill>` 以避免跨分类同名冲突。
    """
    if dest_name is None:
        dest_name = Path(skill_name).name

    project_dir = Path(__file__).parent.resolve()
    skills_dir = project_dir / "skills"

    try:
        url = normalize_git_url(source)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

    if shutil.which("git") is None:
        print("错误: 未找到 git 命令，请先安装 git")
        sys.exit(1)

    tmp = Path(tempfile.mkdtemp(prefix="agents-skills-"))
    try:
        print(f"URL: {url}")
        print(f"Skill: {skill_name}")
        print(f"目标: {skills_dir / dest_name}")
        print()

        # git 命令的进度日志（clone/checkout 等）无需展示，统一静默
        quiet = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 1. clone（无检出、浅克隆、不过滤历史大对象）
        result = subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1", url, "."],
            cwd=str(tmp),
            **quiet,
        )
        if result.returncode != 0:
            print(f"错误: git clone 失败 ({url})")
            sys.exit(1)

        # 2. sparse-checkout 仅拉取 skills/<skill_name>
        result = subprocess.run(
            ["git", "-C", str(tmp), "sparse-checkout", "init", "--cone"],
            **quiet,
        )
        if result.returncode != 0:
            print("错误: git sparse-checkout init 失败")
            sys.exit(1)

        result = subprocess.run(
            ["git", "-C", str(tmp), "sparse-checkout", "set", f"skills/{skill_name}"],
            **quiet,
        )
        if result.returncode != 0:
            print(f"错误: git sparse-checkout set skills/{skill_name} 失败")
            sys.exit(1)

        # 3. 按实际默认分支检出（不写死 main）
        branch = get_default_branch(tmp)
        result = subprocess.run(
            ["git", "-C", str(tmp), "checkout", branch],
            **quiet,
        )
        if result.returncode != 0:
            print(f"错误: git checkout {branch} 失败")
            sys.exit(1)

        # 4. 迁移到项目内 skills/<dest_name>
        src = tmp / "skills" / skill_name
        if not src.exists():
            print(f"错误: 仓库 {url} 中不存在 skills/{skill_name}")
            sys.exit(1)

        skills_dir.mkdir(parents=True, exist_ok=True)
        dest = skills_dir / dest_name
        old_info = None
        if dest.exists():
            old_info = parse_skill_md(dest / "SKILL.md")
            print(f"[覆盖] 已存在 {dest}，将覆盖")
            shutil.rmtree(dest)
        shutil.move(str(src), str(dest))

        # 读取新安装的 SKILL.md 元信息用于回显
        new_info = parse_skill_md(dest / "SKILL.md")
        if new_info:
            if new_info.get("name"):
                print(f"  名称: {new_info['name']}")
            if new_info.get("description"):
                print(f"  描述: {new_info['description']}")
            new_version = new_info.get("version", "")
            if new_version:
                if old_info and old_info.get("version"):
                    if old_info["version"] != new_version:
                        print(f"  版本: {old_info['version']} -> {new_version} (已更新)")
                    else:
                        print(f"  版本: {new_version} (无变更)")
                else:
                    print(f"  版本: {new_version}")
        print(f'Skills "{skill_name}" 安装完成')
        print()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def skills_add(channel: str, skill: str) -> None:
    """通过 git clone + sparse-checkout 安装指定 skill 到项目内 skills/<skill>

    Args:
        channel: skills/prompts 名称（对应 config.yaml 中的 name），或直接 ORG/REPO/URL
        skill: 要安装的 skill 名称（对应仓库 skills/<skill> 目录）
    """
    project_dir = Path(__file__).parent.resolve()
    config = load_config(project_dir)

    # 在 skills 中查找
    matched = None
    for s in config.get("skills", []):
        if s.get("name") == channel:
            matched = s
            break

    # 在 prompts 中查找
    if not matched:
        for p in config.get("prompts", []):
            if p.get("name") == channel:
                matched = p
                break

    if not matched:
        # 无法在 config.yaml 中匹配到渠道时，尝试将 channel 直接作为
        # user/repo 或 URL 使用（如 jetsung/agents）
        source = resolve_source(channel)
        if source:
            git_clone_skill(source, skill)
            return
        print(f"错误: 未找到 channel '{channel}'，请检查 config.yaml 中的 skills 或 prompts 配置")
        sys.exit(1)

    url = matched.get("url")
    if not url:
        print(f"错误: channel '{channel}' 缺少 url 字段")
        sys.exit(1)

    depth = int(matched.get("depth", 1) or 1)
    # depth=1 → 仓库内 skills/<skill>；depth>=2（嵌套）→ skills/<cat>/.../<skill>
    # 用户可能只传末级名称（如 grill-with-docs），需按 depth 解析出完整相对路径
    if depth > 1 and "/" not in skill:
        candidates = [
            it["path"] for it in list_skills_from_repo(url, depth)
            if it.get("name") == skill or it.get("path", "").endswith("/" + skill)
        ]
        if not candidates:
            print(f"错误: 渠道 '{channel}' (depth={depth}) 中未找到 skill '{skill}'")
            print("提示: 可用 `just skill-show {channel}` 查看带路径的 skill 列表".format(channel=channel))
            sys.exit(1)
        if len(candidates) > 1:
            print(f"错误: skill '{skill}' 在多渠道分类中存在，请指定完整路径之一：")
            for c in candidates:
                print(f"  - {c}")
            sys.exit(1)
        skill = candidates[0]

    # 两层渠道以 <cat>/<skill> 形式传入 skill，即为仓库内相对路径；
    # 落盘名仅取末级名称（如 productivity/writing-great-skills → writing-great-skills）
    dest_name = skill.split("/")[-1]
    git_clone_skill(url, skill, dest_name)


def resolve_recommended_source(item: dict, skills: list) -> str:
    """解析 recommended 子项的来源 source

    规则：
      - url 与 name 同时存在时优先使用 url（直接返回完整 URL）
      - 仅 name 时，从同级 skills 模块查找同名渠道取其 url
      - 两者皆缺，或仅 name 且 skills 模块无对应渠道，返回 None
    """
    url = item.get("url")
    if url:
        return url

    name = item.get("name")
    if name:
        for s in skills:
            if s.get("name") == name:
                s_url = s.get("url")
                if s_url:
                    return s_url
        return None

    return None


def install_recommended(project_dir: Path) -> None:
    """根据 config.yaml 的 recommended 模块安装推荐 skills"""
    config = load_config(project_dir)
    recommended = config.get("recommended", [])
    skills = config.get("skills", [])

    if not recommended:
        print("没有配置 recommended")
        return

    print(f"开始安装 {len(recommended)} 个推荐来源...\n")

    for item in recommended:
        name = item.get("name")
        url = item.get("url")
        if not name and not url:
            print("[跳过] 缺少 name 或 url")
            continue

        display_name = name or url
        source = resolve_recommended_source(item, skills)

        if not source:
            print(f"[跳过] {display_name}: 无有效来源（url 缺失，且 skills 模块无对应渠道）")
            continue

        item_skills = item.get("skills", [])
        if not item_skills:
            print(f"[跳过] {name}: 无 skills 列表")
            continue

        print(f"来源: {display_name}")
        for skill in item_skills:
            git_clone_skill(source, skill)
        print()
        print("-" * 80)

    print("推荐 skills 安装完成")


def main():
    parser = argparse.ArgumentParser(description="AI Agents 配置安装工具")
    subparsers = parser.add_subparsers(dest="action", help="执行的动作")

    # install
    p_install = subparsers.add_parser(
        "install",
        help="安装工具：--rec/-r 推荐、--all/-a 全部、或指定 TOOLS ID",
    )
    install_grp = p_install.add_mutually_exclusive_group(required=True)
    install_grp.add_argument("-r", "--rec", action="store_true", help="安装 config.yaml 中 recommended 的推荐 skills")
    install_grp.add_argument("-a", "--all", action="store_true", help="安装 config.yaml 中的全部 tools")
    install_grp.add_argument("skill", nargs="?", help="指定要安装的 TOOLS ID")

    # setup-dir
    subparsers.add_parser("setup-dir", help="将当前目录链接至 ~/.agents")

    # setup-skills
    subparsers.add_parser("setup-skills", help="安装 skills 目录到各 AI 工具")

    # setup-agents
    subparsers.add_parser("setup-agents", help="安装 agents 配置文件到各 AI 工具")

    # setup
    subparsers.add_parser("setup", help="完整初始化（链接 + 安装 skills + 安装 agents）")

    # skills list
    subparsers.add_parser("skills-list", help="列出 config.yaml 中配置的 skills 源")

    # prompts list
    subparsers.add_parser("prompts-list", help="列出 config.yaml 中配置的 prompts 源")

    # skills show
    p_skills_show = subparsers.add_parser("skills-show", help="显示 skills 渠道中可用的 skill 列表（自管 git clone）")
    p_skills_show.add_argument("-a", "--all", action="store_true", help="列出 config.yaml 中所有渠道的 skill")
    p_skills_show.add_argument("channel", nargs="?", default="", help="指定渠道（config name / ORG/REPO / URL），留空需配合 --all 或显示帮助")

    # skills installed
    p_installed = subparsers.add_parser("skills-installed", help="列出已安装的 skills")
    p_installed.add_argument("-a", "--all", action="store_true", help="同时显示每个 skill 的 name/description/version")

    # skills add
    p_add = subparsers.add_parser("skills-add", help="通过 npx skills add 安装指定 skill")
    p_add.add_argument("channel", help="channel 名称（对应 config.yaml 中的 name）")
    p_add.add_argument("skill", help="要安装的 skill 名称")

    # skills remove
    p_remove = subparsers.add_parser("skills-remove", help="移除已安装的 skill（-a 全部 / 指定 <SKILL_PATH>）")
    remove_grp = p_remove.add_mutually_exclusive_group()
    remove_grp.add_argument("-a", "--all", action="store_true", help="删除 skills/ 下的所有 skill")
    remove_grp.add_argument("skill_path", nargs="?", default="", help="指定要删除的 skill 目录名（相对 skills/）")

    # skills find
    p_find = subparsers.add_parser("skills-find", help="搜索 skills")
    p_find.add_argument("query", nargs="?", default="", help="搜索关键词")

    # skills query
    p_query = subparsers.add_parser("skills-query", help="按名称查询单个 skill 的元信息（跨所有渠道或指定渠道）")
    p_query.add_argument("skill", help="要查询的 skill 名称")
    p_query.add_argument("channel", nargs="?", default="", help="可选渠道（config name / ORG/REPO / URL）；留空则跨所有渠道")

    # list
    p_list = subparsers.add_parser("list", help="统一列表入口: just list <skills|prompts|skill|tools>")
    p_list.add_argument("kind", nargs="?", default="", help="列表类型: skills / prompts / skill / tools")

    # recommended
    subparsers.add_parser("recommended", help="根据 config.yaml 的 recommended 模块安装推荐 skills")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    project_dir = Path(__file__).parent.resolve()

    if args.action == "install":
        if args.rec:
            install_recommended(project_dir)
        elif args.all:
            install_skills(project_dir, None)
        else:
            if args.skill == "rec":
                print("请使用 --rec 或 -r 安装推荐 skills")
                sys.exit(1)
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
    elif args.action == "skills-list":
        cmd_skills_list(project_dir)
    elif args.action == "prompts-list":
        cmd_prompts_list(project_dir)
    elif args.action == "skills-show":
        cmd_skills_show(project_dir, args.channel, args.all)
    elif args.action == "skills-installed":
        cmd_skills_installed(args.all)
    elif args.action == "skills-add":
        skills_add(args.channel, args.skill)
    elif args.action == "skills-remove":
        cmd_skills_remove(args.all, args.skill_path)
    elif args.action == "skills-find":
        cmd_skills_find(args.query)
    elif args.action == "skills-query":
        query_skill(project_dir, args.skill, args.channel)
    elif args.action == "list":
        cmd_list(args.kind)
    elif args.action == "recommended":
        install_recommended(project_dir)


if __name__ == "__main__":
    main()
