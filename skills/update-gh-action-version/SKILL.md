# Skill: update-gh-action-version

## 简介
这是一个用于自动更新 GitHub Actions 工作流文件中使用的 Action 版本的辅助脚本。

## 依赖
- 需要安装 `curl` 和 `sed`。

## 调用方式
```bash
/update-gh-action-version [dir] [action]
```

## 参数说明
- `dir`: 可选，要更新的目录路径（默认为 `.github/workflows`）
- `action`: 可选，要更新的 Action 名称（如 `actions/checkout`）

## 示例
更新当前项目 `.github/workflows` 下所有 yaml/yml 文件中所有 Action 的版本：
```bash
/update-gh-action-version
```

更新 `.test/test/` 目录下所有 yaml/yml 文件中所有 Action 的版本：
```bash
/update-gh-action-version .test/test/
```

更新 `.test/test/` 目录下所有 yaml/yml 文件中 `actions/checkout` 的版本：
```bash
/update-gh-action-version .test/test/ actions/checkout
```

## 原理
1. 通过 GitHub API 获取指定 Action 的最新 Release Tag。
2. 提取其主版本号（如 `v4.1.0` -> `v4`）。
3. 使用 `sed` 正则匹配并替换 YAML 文件中对应的版本引用。