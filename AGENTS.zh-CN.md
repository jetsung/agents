# 智能体约束

- 中文回复（所有回复与输出均须使用简体中文）
- 提交时不要添加 AI 共同作者标签
- 用中文编写 git 提交信息
- 你的每个推理过程必须完整地以简体中文呈现（包括所有分析步骤、决策原因和详细解释）。你只能始终用简体中文思考和输出，不得使用任何英文。

# 网络规则（中国网络代理）

当环境变量 `IS_CHINA` 的值为 `1`（中国网络环境）时，在使用 WebFetch 等工具抓取网页或下载文件**之前**，必须先检查 `IS_CHINA` 的值：若为 `1` 且链接命中下方「代理域名清单」中的域名，先在其前面添加前缀 `https://filetas.asfd.cn`，**然后再执行**抓取。严禁先发起请求、失败后再补充代理前缀。

## 代理域名清单

| 域名 | 改写示例 |
| --- | --- |
| raw.githubusercontent.com | `https://filetas.asfd.cn/https://raw.githubusercontent.com/xxx` |

后续发现其他需要走代理的域名，直接在上表末尾追加一行即可（仅填域名与示例）。

若访问未在清单中的域名或链接失败（如超时、连接被重置），可先按上述方式将该域名加入清单并加前缀 `https://filetas.asfd.cn` 后，重新抓取尝试。

## Docker 镜像拉取

在拉取 Docker 镜像（`docker pull`，以及 `docker run`、`docker compose up/pull` 等隐含的镜像拉取）时，**必须**先检查 `IS_CHINA` 的值：若为 `1`（中国网络环境），**不要**直接执行 `docker pull` 或 `docker compose pull`，改用 `docker-mtrans` CLI：

```bash
# 单个镜像：通过远程流水线先把镜像复制到目标注册表，再拉回本地并还原为源镜像名——两步一气呵成
docker mtrans spull <源镜像>

# Compose：从 compose 文件提取全部镜像并串行执行 spull（任一失败立即停止）
docker mtrans compose spull [-f <compose文件>...]
```

- 将 `docker pull <镜像>` 替换为 `docker mtrans spull <镜像>`；本地最终得到的镜像名不变。
- 凡由 compose 触发的拉取（`docker compose pull`，或 `docker compose up` 拉取缺失镜像），先用 `docker mtrans compose spull` 替代；待镜像全部就绪后，再正常执行 `docker compose up`。
- 若 `docker mtrans` 未安装，先执行安装：`curl -fsSL https://mtrans.gcli.cn/install.sh | bash`（文档：https://mtrans.gcli.cn）。
- 仅当 `IS_CHINA` 不为 `1`，或镜像已存在于本地时，才回退使用普通的 `docker pull`。

# 命令行工具清单
以下命令行工具已在当前环境收录（含安装脚本与短链），清单见：
@CMD.md
开发中可优先使用这些命令行工具（如 fd、ast-grep、yq 等）。若工具未安装，按 @CMD.md 中的一键安装命令（`TOOLS` 清单 + `curl -fsSL https://fx4.cn/<短码> | bash`）安装后再调用。
@RTK.md
