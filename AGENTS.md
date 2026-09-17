# Agent Constraints

- Reply in Chinese (all replies and output must use Simplified Chinese)
- Do not add AI co-author tags when committing
- Write git commit messages in Chinese
- Every part of your reasoning must be presented entirely in Simplified Chinese (including all analysis steps, decision rationale, and detailed explanations). You must always think and output only in Simplified Chinese; no English allowed.

# Network Rules (China Network Proxy)

When the environment variable `IS_CHINA` is set to `1` (China network environment), before using tools such as WebFetch to fetch web pages or download files, you **must** first check the value of `IS_CHINA`: if it is `1` and the link matches a domain in the "Proxy Domain List" below, first prepend the prefix `https://filetas.asfd.cn` to it, **then** perform the fetch. Never send the request first and add the proxy prefix only after a failure.

## Proxy Domain List

| Domain | Rewriting Example |
| --- | --- |
| raw.githubusercontent.com | `https://filetas.asfd.cn/https://raw.githubusercontent.com/xxx` |

When other domains that need the proxy are discovered later, simply append a row at the end of the table above (domain and example only).

If you access a domain not in the list or a link fails (e.g. timeout, connection reset), you may first add that domain to the list as described above with the `https://filetas.asfd.cn` prefix, then retry the fetch.

## Docker Image Pull

When pulling Docker images (`docker pull`, images referenced by `docker run`, `docker compose up/pull`, etc.), you **must** first check the value of `IS_CHINA`: if it is `1` (China network environment), do **not** run `docker pull` or `docker compose pull` directly — use the `docker-mtrans` CLI instead:

```bash
# single image: sync to the target registry via remote pipeline, then pull back and rename to the original image name — all in one step
docker mtrans spull <source-image>

# compose: extract all images from the compose file(s) and spull them serially (stops on first failure)
docker mtrans compose spull [-f <compose-file>...]
```

- Replace `docker pull <image>` with `docker mtrans spull <image>`; the local result is the same image name.
- Replace any compose-driven pull (`docker compose pull`, or `docker compose up` pulling missing images) with `docker mtrans compose spull` first, then run `docker compose up` normally once all images are local.
- If `docker mtrans` is not installed, install it first: `curl -fsSL https://mtrans.gcli.cn/install.sh | bash` (docs: https://mtrans.gcli.cn).
- Only fall back to plain `docker pull` when `IS_CHINA` is not `1`, or the image already exists locally.

# Command-Line Tool List
The following command-line tools are already available in this environment (with install scripts and short links); see the list at:
@CMD.md
Prefer these command-line tools during development (e.g. fd, ast-grep, yq, etc.). If a tool is not installed, install it first using the one-line install command in @CMD.md (the `TOOLS` list + `curl -fsSL https://fx4.cn/<shortcode> | bash`), then invoke it.
@RTK.md
