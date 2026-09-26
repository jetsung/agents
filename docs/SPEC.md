# agents.py 功能规格（SPEC）

> 本文档从 `agents.py` 与 `config.yaml` 中提取，描述当前实现的功能行为，供开发与维护参考。
> 如与代码行为不一致，以 `agents.py` 实际实现为准。

## 1. 概述

`agents.py` 是一个单文件 Python 安装器，依据 `config.yaml` 中的声明完成：

- **tools 安装**：下载 / 解压 / 移动等结构化步骤（action），或直接执行 shell 命令（run）
- **平台配置**：将 `AGENTS.md` 链接/安装到各 AI 工具的配置目录
- **`.agents` 目录**：建立项目与 `~/.agents` 的符号链接

依赖：Python 3 标准库 + `PyYAML`。`run` 步骤直接使用 **Linux shell**（`sh -c`），不做 Windows 兼容。

## 2. 命令行（CLI）

```
python3 agents.py <command> [参数]
```

| 命令 | 参数 | 说明 |
|---|---|---|
| `install` | `-a` / `--all` 或 `TOOLS_ID` | 安装 config.yaml 中的 tools（全部或指定 id；等价 `just install`） |
| `agents` | `[target]` | 分发 agents 配置：无参数显示帮助（渠道列表），`all` 全部渠道，或指定渠道 slug |
| `setup` | — | 完整初始化：创建 `.agents` 链接 + 分发 agents 配置 |
| `tools-list` | `[tool_id]` | 列出 config.yaml 中的 tools（传 id 时仅显示该工具） |
| `platforms-list` | `[name]` | 列出平台渠道（内置 + config.yaml 自定义 + xskill 补充） |

justfile 对应关系：`just install <id>` → `install <id>`，`just list <id>` → `tools-list <id>`，
`just agents [all|<slug>]` → `agents [all|<slug>]`，`just platforms` → `platforms-list`。

## 3. config.yaml 结构

```yaml
env: {}          # 全局环境变量，与各工具 env 合并（工具级覆盖全局）
platforms: {}    # 平台渠道配置：path / agents / source / ensure_dir
tools: []        # 工具安装列表
```

### 3.1 tools 条目字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | 工具唯一标识 |
| `name` | ❌ | 显示名称，缺省同 `id` |
| `type` | ❌ | 资源类型：`skill` / `tool`（默认）/ `mcp` / `custom` |
| `env` | ❌ | 工具专属环境变量，支持 `$VAR` 引用全局变量 |
| `steps` | ✅ | 步骤列表（见第 4 节），缺失时安装报错退出 |

### 3.2 type 的含义

| type | run 工作目录（AGENTS_RUN_DIR） | 说明 |
|---|---|---|
| `skill` | `skills/` | 作为 skill 安装到项目内 skills 目录 |
| `mcp` | `mcp/` | MCP 服务 |
| `tool` | `.tmp/` | 普通命令行工具（默认） |
| `custom` | `.tmp/` | 自定义类型，不支持解压，工作全靠 run 步骤 |

## 4. steps 步骤

`steps` 是有序步骤列表，每项为字典。按顺序执行，任一步骤失败即 `sys.exit(1)` 终止。
每个步骤可带可选 `name` 字段作为说明（仅展示）。

步骤分两类：**action 结构化步骤**（推荐）与 **run shell 步骤**。
`action` 与 `run` 字段互斥（详见 4.3）：无 `action` 时默认为 `shell`，必须提供 `run` 字段；
`action` 为其他内置命令时使用 `source`/`target`，忽略 `run`。

### 4.1 action: download — 下载

```yaml
- action: download
  source: $URL            # 下载 URL，支持 $VAR 替换
  target: custom.tgz      # 可选：自定义文件名（支持 $VAR）
```

- 落盘位置：`.tmp/<id>/<文件名>`（固定，暂存用途）
- 文件名来源：指定 `target` 时用 target 名；否则从 URL 路径提取（剥离 query string）
- 完成后导出环境变量 `AGENTS_ARCHIVE` = 实际使用的文件名（供 extract / run 引用）

### 4.2 action: extract — 解压

```yaml
- action: extract
  source: pkg.tgz         # 可选：归档包名，省略时自动用最近一次 download 的归档名
  target: out-dir         # 可选：解压目标目录
```

- `source` 查找顺序：显式指定 → `.tmp/<id>/` 下查找；省略 → `.tmp/<id>/$AGENTS_ARCHIVE`
- `target` 缺省按 type：`skill` → `skills/<id>/`，`mcp` → `mcp/<id>/`，其他 → `.tmp/<id>/`
- **target 已存在时先移除**（保证内容全新）
- **包内唯一顶层目录自动上提**：解压后若目录内只有一个子目录（如 `package/`），
  其内容自动上提到 target，无论包是否含顶层目录，内容都直接落位

### 4.3 内置 actions

`action` 与 `run` 互斥：

- **无 action（默认 `shell`）→ 必须提供 `run` 字段**，执行脚本（行为见 4.4）
- **`action: shell`** → 同样使用 `run` 字段（`run` 必填）
- **`action` 为其他内置命令** → 使用 `source`/`target` 参数，**忽略 `run` 字段**（即使存在）

| action | 参数 | 行为 |
|---|---|---|
| `download` | `source`(URL), `target`(可选文件名) | 下载到 `.tmp/<id>/`，导出 `AGENTS_ARCHIVE` |
| `extract` | `source`(可选), `target`(可选) | 解压（见 4.2） |
| `mv` | `source`, `target` | 移动；**target 已存在时先删除**（避免移成子目录） |
| `cp` | `source`, `target` | 复制（目录用 copytree，文件用 copy2，已存在则覆盖） |
| `rm` | `source`（或 `target`） | 删除文件或目录（递归） |
| `mkdir` | `source`（或 `target`） | 创建目录（`parents=True`） |
| `test` | `source` + 断言字段 | 存在性断言：`exists` / `exists_dir` / `exists_file`，值为 `true`（必须存在）/ `false`（必须不存在），不满足则退出 |
| `shell` | `run`（必填） | 使用 `run` 字段执行脚本，行为同 4.4 |

### 4.4 run — shell 步骤

无 `action`（默认 `shell`）与显式 `action: shell` 共用此执行路径：

```yaml
- name: 安装 XX
  run: |
    npm install -g xx
    xx --version
```

- 整段交给 `sh -c` 执行（Linux shell，支持管道、`&&`、通配符等全部 shell 语法）
- 工作目录为 `AGENTS_RUN_DIR`（按 type 决定，见 3.2）
- 输出捕获后回显：**stdout 前置一个空行**，与安装日志分隔；末尾无换行时自动补上
- 退出码非 0 → 打印失败信息并终止

## 5. 环境变量

| 变量 | 来源 | 值 |
|---|---|---|
| `AGENTS_RUN_DIR` | 自动注入 | 当前工具 run 工作目录绝对路径（按 type） |
| `AGENTS_TOOL_DIR` | 自动注入 | 工具专属目录绝对路径 = `AGENTS_RUN_DIR/type/id`（run_cwd 目录名与 type 同名时去重，如 mcp → `mcp/<id>`） |
| `AGENTS_ARCHIVE` | `download` 步骤导出 | 最近一次下载的归档文件名 |
| config.yaml `env` | 用户声明 | 全局 + 工具级合并，工具级优先 |

注入的变量可通过 `export_env` 写入 `os.environ`（子进程继承），也可在
`run` / `source` / `target` 中以 `$VAR` 形式引用（由 `resolve_env_vars` 替换，
匹配 `$[A-Z_][A-Z0-9_]*`，未定义时原样保留）。

## 6. 路径解析规则（resolve_path_ctx）

action 的 `source` / `target` 相对路径按以下顺序解析：

1. `~` 开头 → 展开为用户主目录
2. 绝对路径 → 原样使用
3. `skills/`、`mcp/`、`.tmp/` 前缀 → 相对**项目根目录**（agents.py 所在目录）
4. 其余 → 相对当前工具的 **AGENTS_RUN_DIR**（skill → `skills/`，mcp → `mcp/`，其他 → `.tmp/`）

## 7. 归档解压（unzip_file）

- **魔数识别，不依赖扩展名**（类似 `file` 命令）：
  - `PK\x03\x04` → zip（zipfile）
  - `\x1f\x8b` → tar.gz（tarfile, `r:gz`）
  - `\xfd7zXZ\x00` → tar.xz（tarfile, `r:xz`）
  - 偏移 257 处 `ustar` → tar（tarfile, `r:`）
  - 无法识别 → 抛 `ValueError` 终止
- tar 系解压使用 `filter="data"` 防路径穿越攻击
- `.tgz` / `.txz` 天然兼容（魔数与 `.tar.gz` / `.tar.xz` 相同）

## 8. 输出样式

- 颜色基于 `sys.stdout.isatty()` 自动降级：非终端（重定向/管道）不输出色码
- `安装工具:` 标题 → **加粗青色**
- 下载/保存/解压/目标 标题、action 标签（`[mv]` `[extract]` 等）→ 青色
- run 输出前仅空行，无 `$ 命令` 前缀
- 完成提示 → 绿色：`MCP "..." 安装完成` / `Skills "..." 安装完成` / `Tool "..." 安装完成`，前置空行
- 末尾汇总按实际安装 type 精确提示：仅 mcp → `mcp 安装完成`，仅 skill → `skills 安装完成`，
  仅 tool/custom → `tools 安装完成`，混合用 ` / ` 连接；带过滤时附 ` (过滤: <id>)`

## 9. 安装流程（install_tools）

1. 读取 config.yaml（`load_config`）
2. `--all` 时取全部 tools，否则按 id 过滤（找不到则报错退出）
3. 逐个工具：
   - 合并环境变量（全局 env → 工具 env → 注入 `AGENTS_RUN_DIR`），`export_env` 写入进程环境
   - 打印 `安装工具: <name>`（加粗青色）
   - 依次执行 steps（见第 4 节）
   - 打印绿色完成提示 + 分隔线
4. 打印末尾汇总（见第 8 节）

## 10. 目录约定

| 目录 | 用途 |
|---|---|
| `.tmp/<id>/` | download 归档暂存（extract 后即弃） |
| `skills/<id>/` | type=skill 的解压落地目录 |
| `mcp/<id>/` | type=mcp 的解压落地目录 |
| `docs/` | 开发文档（本规格 SPEC.md） |

> 完整规格参见 `docs/SPEC.md`；config.yaml 字段级校验见 `config.schema.json`。
