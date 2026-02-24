# 获取当前项目的绝对路径
$PROJECT_DIR = $PSScriptRoot
if (-not $PROJECT_DIR) {
    $PROJECT_DIR = (Get-Location).Path
}

# 定义 ~ 目录
$HOME_DIR = $env:USERPROFILE

# 定义 ~/.agents 目录
$AGENTS_DIR = Join-Path $HOME_DIR ".agents"

# 定义目标 CLI 工具的 skills 目录路径
$SKILLS_TARGETS = @(
    (Join-Path $HOME_DIR ".claude/skills"),
    (Join-Path $HOME_DIR ".opencode/skills"),
    (Join-Path $HOME_DIR ".codex/skills"),
    (Join-Path $HOME_DIR ".iflow/skills"),
    (Join-Path $HOME_DIR ".qwen/skills"),
    (Join-Path $HOME_DIR ".codebuddy/skills"),
    (Join-Path $HOME_DIR ".cline/skills"),
    (Join-Path $HOME_DIR ".kilocode/skills"),
    (Join-Path $HOME_DIR ".roo/skills"),
    (Join-Path $HOME_DIR ".factory/skills"),
    (Join-Path $HOME_DIR ".qoder/skills")
)

# 定义目标 CLI 工具的 agents 配置文件的路径
# 格式: @{ Target = "目标路径"; Source = "源文件相对路径" }
$AGENTS_TARGETS = @(
    @{ Target = (Join-Path $HOME_DIR ".claude/CLAUDE.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".opencode/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".codex/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".iflow/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".qwen/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".codebuddy/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".cline/CLAUDE.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".kilocode/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".roo/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".factory/AGENTS.md"); Source = "AGENTS.md" },
    @{ Target = (Join-Path $HOME_DIR ".qoder/AGENTS.md"); Source = "AGENTS.md" }
)

# 创建链接的通用函数
# 参数: TARGET LINK_NAME
function New-Link {
    param(
        [string]$Target,
        [string]$LinkName
    )

    $ParentDir = Split-Path $LinkName -Parent

    # 1. 检查父目录是否存在（即工具是否已安装/配置）
    if (-not (Test-Path $ParentDir)) {
        Write-Host "[跳过] 父目录不存在: $ParentDir" -ForegroundColor Yellow
        return
    }

    # 2. 检查目标是否已存在
    if (Test-Path $LinkName) {
        $Item = Get-Item $LinkName -Force
        if ($Item.LinkType -eq "SymbolicLink") {
            # 如果是符号链接，判断是否已经指向正确位置
            $CurrentTarget = $Item.Target
            if ($CurrentTarget -eq $Target) {
                Write-Host "[跳过] $LinkName 已经是正确的符号链接。" -ForegroundColor Green
                return
            } else {
                Write-Host "[更新] 更新符号链接: $LinkName -> $Target" -ForegroundColor Cyan
                Remove-Item $LinkName -Force
            }
        } elseif ($Item.PSIsContainer) {
            # 如果是真实目录，进行备份
            $BackupDir = "${LinkName}_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Write-Host "[备份] 发现现有目录，正在备份至: $BackupDir" -ForegroundColor Yellow
            Move-Item $LinkName $BackupDir -Force
        } else {
            # 如果是真实文件，进行备份
            $BackupFile = "${LinkName}_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Write-Host "[备份] 发现现有文件，正在备份至: $BackupFile" -ForegroundColor Yellow
            Move-Item $LinkName $BackupFile -Force
        }
    }

    # 3. 创建符号链接
    # 先尝试使用 mklink 命令
    $cmd = "cmd /c mklink /D `"$LinkName`" `"$Target`""
    $result = cmd /c $cmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[成功] 已链接: $LinkName -> $Target" -ForegroundColor Green
        return
    } else {
        Write-Host "[失败] 无法链接: $LinkName (可能需要管理员权限)" -ForegroundColor Red
    }
}

# 安装 agents 目录的函数
function Install-AgentsDir {
    Write-Host "当前项目路径: $PROJECT_DIR"
    Write-Host "Agents 目录: $AGENTS_DIR"
    Write-Host "开始建立链接..."

    # 1. 检查当前目录是否在 ~/.agents 目录
    if ($PROJECT_DIR -eq $AGENTS_DIR) {
        Write-Host "[信息] 当前目录已在 ~/.agents，跳过链接创建。" -ForegroundColor Green
        return
    }

    # 2. 如果不在，检查 ~/.agents 是否已存在
    if (Test-Path $AGENTS_DIR) {
        $Item = Get-Item $AGENTS_DIR -Force
        if ($Item.LinkType -eq "SymbolicLink") {
            # 已是符号链接，检查是否指向正确位置
            $CurrentTarget = $Item.Target
            if ($CurrentTarget -eq $PROJECT_DIR) {
                Write-Host "[跳过] ~/.agents 已正确链接到当前目录。" -ForegroundColor Green
            } else {
                Write-Host "[更新] 更新 ~/.agents 链接: $AGENTS_DIR -> $PROJECT_DIR" -ForegroundColor Cyan
                Remove-Item $AGENTS_DIR -Force
                New-Link -Target $PROJECT_DIR -LinkName $AGENTS_DIR
            }
        } else {
            # 是真实目录，进行备份
            $BackupDir = "${AGENTS_DIR}_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Write-Host "[备份] 发现现有目录，正在备份至: $BackupDir" -ForegroundColor Yellow
            Move-Item $AGENTS_DIR $BackupDir -Force
            New-Link -Target $PROJECT_DIR -LinkName $AGENTS_DIR
        }
    } else {
        # 不存在，直接创建链接
        New-Link -Target $PROJECT_DIR -LinkName $AGENTS_DIR
    }

    Write-Host "完成！" -ForegroundColor Green
}

# 安装 skills 的函数
function Install-Skills {
    # 检查 ~/.agents 是否存在，如果不存在则自动创建
    if (-not (Test-Path $AGENTS_DIR)) {
        Write-Host "[信息] ~/.agents 不存在，正在自动创建..." -ForegroundColor Yellow
        Install-AgentsDir
    }

    Write-Host "以 ~/.agents 为基准安装 skills..."
    Write-Host "开始建立链接..."

    $SkillsSource = Join-Path $AGENTS_DIR "skills"
    foreach ($Target in $SKILLS_TARGETS) {
        New-Link -Target $SkillsSource -LinkName $Target
    }

    Write-Host "完成！" -ForegroundColor Green
}

# 安装 agents 配置文件的函数
function Install-Agents {
    # 检查 ~/.agents 是否存在，如果不存在则自动创建
    if (-not (Test-Path $AGENTS_DIR)) {
        Write-Host "[信息] ~/.agents 不存在，正在自动创建..." -ForegroundColor Yellow
        Install-AgentsDir
    }

    Write-Host "以 ~/.agents 为基准安装 agents 配置文件..."
    Write-Host "开始建立链接..."

    foreach ($TargetInfo in $AGENTS_TARGETS) {
        $Target = $TargetInfo.Target
        $SourceFile = $TargetInfo.Source
        $SourcePath = Join-Path $AGENTS_DIR $SourceFile

        # 检查源文件是否存在于 ~/.agents 目录
        if (-not (Test-Path $SourcePath)) {
            Write-Host "[跳过] 源文件不存在: $SourcePath" -ForegroundColor Yellow
            continue
        }

        New-Link -Target $SourcePath -LinkName $Target
    }

    Write-Host "完成！" -ForegroundColor Green
}

# 显示帮助信息
function Show-Help {
    Write-Host "用法: .\install.ps1 [-Action ACTION]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "选项:" -ForegroundColor White
    Write-Host "  -Action ACTION    执行指定动作"
    Write-Host "                   支持的动作:"
    Write-Host "                     agents-dir - 将当前目录链接至 ~/.agents"
    Write-Host "                     skills     - 安装 skills 目录"
    Write-Host "                     agents     - 安装 agents 配置文件"
    Write-Host "  -Help             显示此帮助信息"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor White
    Write-Host "  .\install.ps1 -Action agents-dir - 将当前目录链接至 ~/.agents"
    Write-Host "  .\install.ps1 -Action skills     - 安装 skills 目录"
    Write-Host "  .\install.ps1 -Action agents     - 安装 agents 配置文件"
}

# 解析命令行参数
$Action = ""
$ShowHelp = $false

if ($args.Count -eq 0) {
    Show-Help
    exit 0
}

for ($i = 0; $i -lt $args.Count; $i++) {
    $arg = $args[$i]
    if ($arg -eq "-Action" -or $arg -eq "--action" -or $arg -eq "-a") {
        if ($i + 1 -lt $args.Count) {
            $Action = $args[$i + 1]
            $i++
        }
    } elseif ($arg -eq "-Help" -or $arg -eq "--help" -or $arg -eq "-h") {
        $ShowHelp = $true
    } else {
        Write-Host "未知选项: $arg" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

if ($ShowHelp) {
    Show-Help
    exit 0
}

# 根据动作执行相应功能
switch ($Action) {
    "agents-dir" {
        Install-AgentsDir
    }
    "skills" {
        Install-Skills
    }
    "agents" {
        Install-Agents
    }
    "" {
        Write-Host "错误: 未指定动作。请使用 -Action 指定动作。" -ForegroundColor Red
        Show-Help
        exit 1
    }
    default {
        Write-Host "错误: 不支持的动作 '$Action'。" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
