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

import sys

# 禁止生成 __pycache__（.pyc 字节码缓存）
# 必须在其他 import 之前设置，否则已 import 的模块仍会写缓存
sys.dont_write_bytecode = True

import json
import yaml
import subprocess
import os
import argparse
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime

# ==================== 工具函数 ====================

# ANSI 颜色（非 TTY 输出时自动禁用，避免日志文件中出现色码）
_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    """给文本加 ANSI 颜色码，非终端环境下原样返回"""
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def bold(text: str) -> str:
    """加粗（标题类信息）"""
    return _c("1", text)


def dim(text: str) -> str:
    """暗灰色（次要信息，如 run 的命令内容）"""
    return _c("90", text)


def cyan(text: str) -> str:
    """青色（步骤标题/提示）"""
    return _c("36", text)


def green(text: str) -> str:
    """绿色（完成/成功提示）"""
    return _c("32", text)


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


def display_width(s: str) -> int:
    """计算字符串在终端中的显示宽度（CJK 全角字符计 2，ASCII 计 1）"""
    width = 0
    for ch in s:
        cp = ord(ch)
        # CJK 统一表意文字、全角标点、CJK 符号等
        if (0x2E80 <= cp <= 0x9FFF or
            0xA000 <= cp <= 0xA4CF or
            0xF900 <= cp <= 0xFAFF or
            0xFE30 <= cp <= 0xFE6F or
            0xFF00 <= cp <= 0xFFEF or
            0x20000 <= cp <= 0x2FFFF or
            0x30000 <= cp <= 0x3FFFF):
            width += 2
        else:
            width += 1
    return width


def pad_display(s: str, width: int) -> str:
    """将字符串填充到指定显示宽度（右对齐），不足补空格"""
    current = display_width(s)
    if current >= width:
        return s
    return s + " " * (width - current)


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

# 渠道清单与 ../xskill/docs/PLATFORMS.md 保持一致（单一出处）：
# 全部 27 个渠道写死于此，无需在 config.yaml 重复配置即可安装；
# config.yaml 仍可覆盖同名渠道，~/.xskill/settings.json 仍可补充新渠道。
# 合并优先级：config.yaml 显式配置 > 内置渠道 > ~/.xskill/settings.json 补充。
#
# 说明：
# - path 统一为 ~/.xxx 形式；agents 为相对 path 的 agents 配置文件名。
# - pi（https://github.com/earendil-works/pi-coding-agent）
#   上下文文件（全局）：~/.pi/agent/AGENTS.md
BUILTIN_PLATFORMS = {
    # —— 常用渠道（默认启用，同 PLATFORMS.md）——
    "antigravity": {"name": "Antigravity", "path": "~/.gemini", "agents": "GEMINI.md"},
    "claude": {"name": "Claude Code", "path": "~/.claude", "agents": "CLAUDE.md"},
    "codebuddy": {"name": "CodeBuddy", "path": "~/.codebuddy", "agents": "CODEBUDDY.md"},
    "codex": {"name": "Codex", "path": "~/.codex", "agents": "AGENTS.md"},
    "dsh": {"name": "DeepSeek Harness", "path": "~/.dsh", "agents": "AGENTS.md"},
    "omp": {
        "name": "Oh My Pi",
        "path": "~/.omp/agent",
        "agents": "AGENTS.md",
        "ensure_dir": True,
    },
    "opencode": {"name": "OpenCode", "path": "~/.opencode", "agents": "AGENTS.md"},
    "pi": {
        "name": "Pi",
        "path": "~/.pi/agent",
        "agents": "AGENTS.md",
        "ensure_dir": True,
    },
    "qoder": {"name": "Qoder", "path": "~/.qoder", "agents": "AGENTS.md"},
    "qoder-cn": {"name": "Qoder CN", "path": "~/.qoder-cn", "agents": "AGENTS.md"},
    "workbuddy": {"name": "WorkBuddy", "path": "~/.workbuddy", "agents": "CODEBUDDY.md"},
    "zcode": {"name": "ZCode", "path": "~/.zcode", "agents": "AGENTS.md"},
    # —— 非常用渠道（默认禁用，同 PLATFORMS.md）——
    "commandcode": {"name": "Command Code", "path": "~/.commandcode", "agents": "AGENTS.md"},
    "atomcode": {"name": "AtomCode", "path": "~/.atomcode", "agents": "ATOMCODE.md"},
    "cline": {"name": "Cline", "path": "~/.cline", "agents": "CLAUDE.md"},
    "factory": {"name": "Factory", "path": "~/.factory", "agents": "AGENTS.md"},
    "jcode": {"name": "JCode", "path": "~/.jcode", "agents": "AGENTS.md"},
    "kilo": {"name": "Kilo Code", "path": "~/.kilocode", "agents": "AGENTS.md"},
    "kiro": {"name": "Kiro", "path": "~/.kiro", "agents": "AGENTS.md"},
    "langcli": {"name": "LangCLI", "path": "~/.langcli", "agents": "LANGCLI.md"},
    "openclaude": {"name": "OpenClaude", "path": "~/.openclaude", "agents": "CLAUDE.md"},
    "openinterpreter": {"name": "Open Interpreter", "path": "~/.openinterpreter", "agents": "AGENTS.md"},
    "grok": {"name": "Grok Build CLI", "path": "~/.grok", "agents": "AGENTS.md"},
    "qwen": {"name": "Qwen", "path": "~/.qwen", "agents": "AGENTS.md"},
    # zoo（Zoo Code）接手已停服的 Roo Code，配置目录沿用 ~/.roo
    "zoo": {"name": "Zoo Code", "path": "~/.roo", "agents": "AGENTS.md"},
    # mimocode（MiMo Code）全局配置目录为 ~/.config/mimocode/skills
    "mimocode": {"name": "MiMo Code", "path": "~/.config/mimocode", "agents": "AGENTS.md"},
    # agentty（Agentty）全局配置目录为 ~/.agentty/skills，兼容 .agents/ 规范目录
    "agentty": {"name": "Agentty", "path": "~/.agentty", "agents": "AGENTS.md"},
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


def setup_agents_config(only_platform: str = None) -> None:
    """安装 agents 配置文件到各 AI 工具

    Args:
        only_platform: 可选渠道 slug（platforms 字典的键），
            指定时仅分发该渠道；None 分发全部渠道。
    """
    project_dir = Path(__file__).parent.resolve()
    agents_dir = expand_path("~/.agents").resolve()

    # 检查 ~/.agents 是否存在
    if not agents_dir.exists():
        print("[信息] ~/.agents 不存在，正在自动创建...")
        create_agents_dir_link()

    # 合并平台配置：config.yaml > 内置渠道 > ~/.xskill/settings.json 补充
    platforms = load_platforms(project_dir)

    # 指定渠道时校验其存在
    if only_platform and only_platform not in platforms:
        print(f"错误: 未找到渠道 '{only_platform}'")
        print(f"可用渠道: {', '.join(platforms.keys())}")
        sys.exit(1)
    selected = platforms.items() if not only_platform else [(only_platform, platforms[only_platform])]

    print("以 ~/.agents 为基准安装 agents 配置文件...")
    print("开始建立软链接...")

    for name, platform in selected:
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
    """下载文件"""
    print(f"  {cyan('下载:')} {url}")
    urllib.request.urlretrieve(url, str(dest))
    print(f"  {cyan('保存:')} {dest}")


def detect_archive_kind(src: Path) -> str:
    """按文件头魔数识别归档类型（类似 file 命令），不依赖扩展名

    返回 "zip" / "tar.gz" / "tar.xz" / "tar"，未知格式返回 "unknown"。
    """
    with open(str(src), "rb") as fh:
        head = fh.read(6)
        fh.seek(257)
        ustar = fh.read(5)
    if head.startswith(b"PK\x03\x04"):
        return "zip"
    if head.startswith(b"\x1f\x8b"):
        return "tar.gz"
    if head.startswith(b"\xfd7zXZ\x00"):
        return "tar.xz"
    if ustar == b"ustar":
        return "tar"
    return "unknown"


def unzip_file(src: Path, dest: Path) -> None:
    """解压 zip / tar.gz / tar.xz / tar 归档（按魔数识别，跨平台）"""
    print(f"  {cyan('解压:')} {src}")
    kind = detect_archive_kind(src)
    if kind == "zip":
        with zipfile.ZipFile(str(src), "r") as zip_ref:
            zip_ref.extractall(str(dest))
    elif kind in ("tar.gz", "tar.xz", "tar"):
        mode = {"tar.gz": "r:gz", "tar.xz": "r:xz", "tar": "r:"}[kind]
        with tarfile.open(str(src), mode) as tar:
            tar.extractall(str(dest), filter="data")
    else:
        raise ValueError(f"无法识别的归档格式: {src}")
    print(f"  {cyan('目标:')} {dest}")


def get_run_cwd(project_dir: Path, tool_type: str) -> Path:
    """run 步骤的工作目录按 type 决定：skill → skills/，mcp → mcp/，其他 → .tmp"""
    if tool_type == "skill":
        return project_dir / "skills"
    if tool_type == "mcp":
        return project_dir / "mcp"
    return project_dir / ".tmp"


def get_tool_dir(project_dir: Path, tool_type: str, tool_id: str) -> Path:
    """工具专属目录：AGENTS_RUN_DIR/type/id（run_cwd 与 type 同名时去重）

    mcp → mcp/<id>（run_cwd 已是 mcp/，避免 mcp/mcp）；
    skill → skills/skill/<id>；tool/custom → .tmp/tool/<id>。
    """
    run_dir = get_run_cwd(project_dir, tool_type)
    if run_dir.name == tool_type:
        return run_dir / tool_id
    return run_dir / tool_type / tool_id


def resolve_path_ctx(path_str: str, run_cwd: Path, project_dir: Path, tmp_dir: Path) -> Path:
    """把 run 命令中的路径解析为绝对 Path

    规则：~ 开头 → 用户目录展开；绝对路径 → 原样；
    其他相对路径按当前工具类型的 run_cwd 解析（skill → skills/，mcp → mcp/，
    tool/custom → .tmp），同时兼容 skills/、mcp/、.tmp/ 前缀直接落到项目根。
    """
    expanded = os.path.expanduser(path_str)
    p = Path(expanded)
    if p.is_absolute():
        return p
    parts = p.parts
    if parts and parts[0] in ("skills", "mcp", ".tmp"):
        return project_dir / p
    return run_cwd / p


def execute_action(step: dict, run_cwd: Path, project_dir: Path, tmp_dir: Path, env_vars: dict,
                   tool_type: str = "tool", tool_id: str = "") -> None:
    """执行 action 单操作步骤（Linux 文件命令的结构化写法）

    Args:
        step: 步骤字典，含 action 及其参数：
            - download: source 为 URL；target 为目标文件夹（缺省为
              AGENTS_RUN_DIR/type/id 组合目录），文件名取 URL 最后一段
            - mv/cp:    source, target
            - rm:       source（target 可选，多个用 rm 多条）
            - mkdir:    source（或 target）
            - test:     source + target 为期望存在性（exists_dir/exists_file 可选断言）
        run_cwd: 工作目录（相对路径基于它解析）
        project_dir: 项目根目录（skills/ mcp/ .tmp/ 前缀相对它）
        tmp_dir: 临时目录
        env_vars: 环境变量（source/target 支持 $VAR 替换）
        tool_type: 工具类型（download 缺省目标目录组合用）
        tool_id: 工具 id（download 缺省目标目录组合用）
    """
    import shlex

    action = step["action"]

    def rp(key: str) -> Path:
        raw = step.get(key)
        if raw is None:
            return None
        resolved = resolve_env_vars(str(raw), env_vars)
        return resolve_path_ctx(resolved, run_cwd, project_dir, tmp_dir)

    if action == "download":
        url = resolve_env_vars(str(step.get("source", "")), env_vars)
        if not url:
            print(f"action download 需要 source: {step}")
            sys.exit(1)
        # 文件名（软件包名）：target 指定时直接作为文件名（支持 $VAR，相对 .tmp/<id>/ 解析），
        # 未指定时从 URL 路径提取（剥离 query）
        filename = step.get("target")
        if filename:
            filename = resolve_env_vars(str(filename), env_vars)
            dest_dir = tmp_dir / tool_id
        else:
            filename = url.split("/")[-1].split("?")[0]
            dest_dir = project_dir / ".tmp" / tool_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / filename
        download_file(url, dest_file)
        # 导出归档文件名，供后续 extract 省略 source 时使用
        env_vars["AGENTS_ARCHIVE"] = filename
        export_env({"AGENTS_ARCHIVE": filename})
        return
    if action == "extract":
        # 解压归档：source 为包路径，省略时自动使用最近一次 download 的归档名
        # （在 .tmp/<id>/ 下查找）；否则优先按 .tmp/<id>/ 解析，其次通用规则；
        # target 为解压目录（缺省按 type：skill → skills/<id>/，mcp → mcp/<id>/）
        raw_source = step.get("source")
        src = rp("source")
        if src is None and not raw_source:
            last = env_vars.get("AGENTS_ARCHIVE")
            if last:
                src = tmp_dir / tool_id / last
        if src is None or not src.exists():
            if not raw_source:
                print(f"action extract 需要 source（归档文件）: {step}")
                sys.exit(1)
            src = tmp_dir / tool_id / str(raw_source)
        if not src.exists() or src.is_dir():
            print(f"action extract 需要 source（归档文件）: {step}")
            sys.exit(1)
        dest_dir = rp("target")
        if dest_dir is None:
            if tool_type == "skill":
                dest_dir = project_dir / "skills" / tool_id
            elif tool_type == "mcp":
                dest_dir = project_dir / "mcp" / tool_id
            else:
                dest_dir = tmp_dir / tool_id
        # target 已存在则先移除，保证内容全新
        # （若归档本身位于 target 内——如 tool 类型缺省 target=.tmp/<id>/ 与归档同目录——
        #   先把归档挪到临时位置，避免清理 target 时把包删掉）
        if dest_dir == src.parent or dest_dir in src.parents:
            staged = tmp_dir / f".extract_stage_{src.name}"
            shutil.move(str(src), str(staged))
            src = staged
        if dest_dir.is_dir():
            shutil.rmtree(str(dest_dir))
        elif dest_dir.exists():
            dest_dir.unlink()
        dest_dir.mkdir(parents=True, exist_ok=True)
        unzip_file(src, dest_dir)

        # 归档结构适配：若包内所有内容本身包在一层同名/唯一文件夹里，
        # 则把该文件夹内容上提到 target，避免出现 target/pkg/... 双层
        entries = [e for e in dest_dir.iterdir()]
        if len(entries) == 1 and entries[0].is_dir():
            inner = entries[0]
            tmp_stage = dest_dir.parent / f".extract_{dest_dir.name}"
            shutil.move(str(inner), str(tmp_stage))
            shutil.rmtree(str(dest_dir))
            tmp_stage.rename(str(dest_dir))
            print(f"  [{cyan('extract')}] 上提内层目录: {inner.name} -> {dest_dir}")
        return
    if action in ("mv", "cp"):
        src, dest = rp("source"), rp("target")
        if src is None or dest is None:
            print(f"action {action} 需要 source 和 target: {step}")
            sys.exit(1)
        if action == "mv":
            # 先删除已存在的 target，避免 mv 把 src 移成 target 的子目录
            if dest.is_dir():
                shutil.rmtree(str(dest))
            elif dest.exists():
                dest.unlink()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if action == "mv":
            shutil.move(str(src), str(dest))
        elif src.is_dir():
            shutil.copytree(str(src), str(dest), dirs_exist_ok=True)
        else:
            shutil.copy2(str(src), str(dest))
        print(f"  [{cyan(action)}] {src} -> {dest}")
    elif action == "rm":
        target = rp("source") or rp("target")
        if target is None:
            print(f"action rm 需要 source: {step}")
            sys.exit(1)
        if target.is_dir():
            shutil.rmtree(str(target))
        elif target.exists():
            target.unlink()
        print(f"  [{cyan('rm')}] {target}")
    elif action == "mkdir":
        target = rp("source") or rp("target")
        if target is None:
            print(f"action mkdir 需要 source: {step}")
            sys.exit(1)
        target.mkdir(parents=True, exist_ok=True)
        print(f"  [{cyan('mkdir')}] {target}")
    elif action == "test":
        # 断言：exists_dir / exists_file / exists 任填其一（true=必须存在，false=必须不存在）
        src = rp("source")
        checks = [
            ("目录", lambda: src.is_dir(), step.get("exists_dir")),
            ("文件", lambda: src.is_file(), step.get("exists_file")),
            ("存在", lambda: src.exists(), step.get("exists")),
        ]
        for label, fn, expected in checks:
            if expected is None:
                continue
            if fn() is not bool(expected):
                print(f"action test 失败: {src} 期望{'存在' if expected else '不存在'}（{label}）")
                sys.exit(1)
        print(f"  [{cyan('test')}] {src} OK")
    elif action == "shell":
        # action: shell —— 使用 run 字段执行脚本（run 必填；source 不参与）
        cmd_str = step.get("run")
        if not cmd_str:
            print(f"action shell 需要 run 字段: {step}")
            sys.exit(1)
        cmd = resolve_env_vars(str(cmd_str), env_vars)
        result = subprocess.run(cmd, shell=True, cwd=str(run_cwd), capture_output=True, text=True)
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
        if result.returncode != 0:
            print(f"命令执行失败: {cmd}")
            sys.exit(1)
    else:
        print(f"未知 action: {action}")
        sys.exit(1)


def execute_steps(steps: list, env_vars: dict, project_dir: Path, tool_type: str = "tool",
                  tool_id: str = "") -> None:
    """执行安装步骤（支持跨平台命令）

    Args:
        steps: 步骤列表
        env_vars: 环境变量
        project_dir: 项目根目录
        tool_type: 工具类型（skill/tool/mcp/custom），决定 extract 缺省行为
        tool_id: 工具 id（action download 缺省目标目录组合用）
    """
    tmp_dir = project_dir / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    run_cwd = get_run_cwd(project_dir, tool_type)
    run_cwd.mkdir(parents=True, exist_ok=True)

    for step in steps:
        if isinstance(step, str):
            # 旧格式：shell 命令字符串
            resolved = resolve_env_vars(step, env_vars)
            result = subprocess.run(
                resolved,
                shell=True,
                cwd=str(run_cwd),
                capture_output=False,
                text=True,
            )
            if result.returncode != 0:
                print(f"命令执行失败: {resolved}")
                sys.exit(1)
        elif isinstance(step, dict):
            # 字典步骤：action 与 run 互斥
            # - 无 action（默认 shell）→ 必须有 run 字段，执行脚本
            # - action: shell → 同样使用 run 字段
            # - action: 其他内置命令 → 忽略 run 字段，走 execute_action
            if "action" not in step and "run" not in step:
                print(f"步骤缺少 run 字段（无 action 时默认 shell，run 必填）: {step}")
                sys.exit(1)
            if "action" in step:
                execute_action(step, run_cwd, project_dir, tmp_dir, env_vars, tool_type, tool_id)
            else:
                run_cmd = resolve_env_vars(step["run"], env_vars)
                print()  # 命令输出前空一行，便于区分
                result = subprocess.run(
                    run_cmd,
                    shell=True,
                    cwd=str(run_cwd),
                    capture_output=True,
                    text=True,
                )
                # 回显命令输出，末尾无换行时补上，避免与后续输出粘连
                if result.stdout:
                    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
                if result.stderr:
                    print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
                if result.returncode != 0:
                    print(f"命令执行失败: {run_cmd}")
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

    installed_types = set()
    for tool in tools:
        tool_id = tool.get("id")
        if not tool_id:
            print("错误: 工具缺少 id 字段")
            sys.exit(1)

        tool_name = tool.get("name", tool_id)
        tool_type = tool.get("type", "tool")
        tool_env = tool.get("env") or {}
        steps = tool.get("steps")

        installed_types.add(tool_type)

        # 合并环境变量，并注入当前工具 run 工作目录及工具专属目录的绝对路径
        merged_env = {**global_env, **tool_env}
        merged_env["AGENTS_RUN_DIR"] = str(get_run_cwd(project_dir, tool_type).absolute())
        merged_env["AGENTS_TOOL_DIR"] = str(get_tool_dir(project_dir, tool_type, tool_id).absolute())
        export_env(merged_env)

        print(f"{bold(cyan('安装工具:'))} {tool_name}")

        if not steps:
            print(f"错误: 工具 {tool_id} 缺少 steps 字段")
            sys.exit(1)
        execute_steps(steps, merged_env, project_dir, tool_type, tool_id)

        print()
        if tool_type == "skill":
            print(green(f'Skills "{tool_name}" 安装完成'))
        elif tool_type == "mcp":
            print(green(f'MCP "{tool_name}" 安装完成'))
        else:
            print(green(f'Tool "{tool_name}" 安装完成'))
        print()
        print("-" * 80)

    suffix = f" (过滤: {tool_filter})" if tool_filter else ""
    # 末尾汇总按实际安装的 type 精确提示
    type_label = {"skill": "skills", "mcp": "mcp", "tool": "tools", "custom": "tools"}
    if not installed_types:
        print(f"未安装任何工具{suffix}")
    elif len(installed_types) == 1:
        print(f"{type_label[next(iter(installed_types))]} 安装完成{suffix}")
    else:
        labels = " / ".join(sorted(type_label[t] for t in installed_types))
        print(f"{labels} 安装完成{suffix}")
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

    print(f'{"渠道":<16} {"名称":<20} {"目标路径":<46} {"agents":<12} {"来源":<12} {"存在"}')
    print("-" * 120)
    for pname, platform in platforms.items():
        name = platform.get("name") or pname
        agents = platform.get("agents") or "-"
        path = str(expand_platform_path(platform.get("path", ""), project_dir))
        src = platform.get("_source", "config.yaml")
        exists = "存在" if Path(path).exists() else "缺失"
        line = (
            f"{pad_display(pname, 16)} "
            f"{pad_display(name, 20)} "
            f"{pad_display(path, 46)} "
            f"{pad_display(agents, 12)} "
            f"{pad_display(src, 12)} "
            f"{exists}"
        )
        if exists == "缺失" and use_color:
            # 目录缺失：整行标红
            line = f"\033[31m{line}\033[0m"
        print(line)


def cmd_agents(project_dir: Path, target: str = None) -> None:
    """agents 子命令入口

    Args:
        target: None / "all" → 分发到全部渠道；渠道 slug → 仅分发该渠道；
            其他情况打印帮助（列出可用渠道 slug）。
    """
    platforms = load_platforms(project_dir)

    if target in (None, ""):
        # 无参数：显示帮助（列出渠道）
        print("用法: just agents all | just agents <SLUG>")
        print()
        print(f'{"渠道":<16} {"名称":<20} 目标路径')
        print("-" * 80)
        for name, platform in platforms.items():
            print(f'{name:<16} {platform.get("name", name):<20} {expand_platform_path(platform.get("path", ""), project_dir)}')
        return

    if target == "all":
        setup_agents_config(None)
    else:
        setup_agents_config(target)


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

    # agents
    p_agents = subparsers.add_parser(
        "agents",
        help="分发 agents 配置：无参数显示帮助，all 全部渠道，或指定渠道 slug",
    )
    p_agents.add_argument("target", nargs="?", default="", help="all 或渠道 slug，缺省显示帮助")

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
    elif args.action == "agents":
        cmd_agents(project_dir, args.target or None)
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
