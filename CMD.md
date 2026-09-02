# 命令行工具清单（CMD.md）

本文件记录当前环境已收录的命令行工具，供 AI 在开发中选用、安装与调用。

- 每个工具均可通过短链一键安装：`curl -fsSL https://fx4.cn/<短码> | bash`
- **短码** = 短链 URL 中的名称；命令名与短码相同时二者一致，不同名时在下方工具列表的说明中注明
- 已安装的工具可直接使用；未安装的按下方一键安装命令安装后再调用

## 一键安装（幂等：已安装自动跳过）

`TOOLS` 为「短码 命令名」清单：命令名与短码**同名时只写一个词**，不同名时写作 `短码 命令名`。新增工具追加一行即可。

```bash
# 短码 命令名（同名只需一个词；不同名写作“短码 命令名”）
TOOLS="
ag ast-grep
bat
bottom
difft
dust
eza
fd
jed
lsd
procs
rg
rtk
yq
"

while read -r short bin; do
    [[ -z "$short" ]] && continue  # 跳过空行
    bin="${bin:-$short}"          # 缺省时命令名=短码
    if command -v "$bin" >/dev/null 2>&1; then
        echo "✔ $bin 已安装，跳过"
        continue
    fi
    echo "→ 安装 $bin ($short) ..."
    curl -fsSL "https://fx4.cn/${short}" | bash
    echo ""
done <<< "$TOOLS"

echo "全部完成！"
```

## 工具列表

每项三行：**命令名 / 源码 URL / 描述**。

- ast-grep
  https://github.com/ast-grep/ast-grep
  基于语法树的代码结构搜索、lint 与重写 CLI 工具（ast-grep）

- bat
  https://github.com/sharkdp/bat
  带语法高亮的 cat 增强工具

- bottom
  https://github.com/ClementTsang/bottom
  跨平台的图形化进程/系统监控工具

- difft
  https://github.com/Wilfred/difftastic
  能理解语法的结构化 diff 工具

- dust
  https://github.com/bootandy/dust
  用 Rust 编写的更直观的磁盘占用分析（du）工具

- eza
  https://github.com/eza-community/eza
  ls 的现代替代工具

- fd
  https://github.com/sharkdp/fd
  简单快速的 find 替代工具

- jed
  https://github.com/camilomatajira/jed
  用 sed 语法处理 JSON 的命令行工具

- lsd
  https://github.com/lsd-rs/lsd
  下一代 ls 命令：彩色、带图标、更现代的目录列表工具

- procs
  https://github.com/dalance/procs
  用 Rust 编写的现代 ps 进程查看替代工具

- rg
  https://github.com/BurntSushi/ripgrep
  极速递归搜索文件内容的正则工具，遵循 gitignore 规则

- rtk
  https://github.com/rtk-ai/rtk
  降低 LLM token 消耗的 CLI 代理工具

- yq
  https://github.com/mikefarah/yq
  便携式命令行 YAML/JSON/XML/CSV/TOML 等多种格式处理工具
