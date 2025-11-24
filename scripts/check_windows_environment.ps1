# ===================================================================
# Windows Server 环境检测脚本
# 用途：自动检测Windows服务器环境，确认所有依赖是否安装
# ===================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  10U战神滚仓策略 - 环境检测工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 检测函数
function Test-Command {
    param($CommandName)
    try {
        if (Get-Command $CommandName -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Get-Version {
    param($Command, $VersionArg = "--version")
    try {
        $output = & $Command $VersionArg 2>&1 | Out-String
        return $output.Trim()
    } catch {
        return "无法获取版本"
    }
}

# ===================================================================
# 1. 检测 Node.js
# ===================================================================
Write-Host "[1/8] 检测 Node.js..." -ForegroundColor Yellow
if (Test-Command "node") {
    $nodeVersion = Get-Version "node" "-v"
    Write-Host "  ✓ Node.js 已安装: $nodeVersion" -ForegroundColor Green
    
    # 检查版本是否 >= 18
    $versionNumber = $nodeVersion -replace 'v', '' -replace '\..*', ''
    if ([int]$versionNumber -lt 18) {
        Write-Host "  ⚠ 警告: Node.js 版本过低，建议升级到 v18 或更高版本" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Node.js 未安装" -ForegroundColor Red
    Write-Host "    下载地址: https://nodejs.org/" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 2. 检测 npm/pnpm
# ===================================================================
Write-Host "[2/8] 检测 npm/pnpm..." -ForegroundColor Yellow
if (Test-Command "npm") {
    $npmVersion = Get-Version "npm" "-v"
    Write-Host "  ✓ npm 已安装: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ npm 未安装" -ForegroundColor Red
    $allPassed = $false
}

if (Test-Command "pnpm") {
    $pnpmVersion = Get-Version "pnpm" "-v"
    Write-Host "  ✓ pnpm 已安装: v$pnpmVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠ pnpm 未安装（推荐安装）" -ForegroundColor Yellow
    Write-Host "    安装命令: npm install -g pnpm" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# 3. 检测 Python
# ===================================================================
Write-Host "[3/8] 检测 Python..." -ForegroundColor Yellow
if (Test-Command "python") {
    $pythonVersion = Get-Version "python" "--version"
    Write-Host "  ✓ Python 已安装: $pythonVersion" -ForegroundColor Green
    
    # 检查版本是否 >= 3.8
    $versionMatch = $pythonVersion -match 'Python (\d+)\.(\d+)'
    if ($versionMatch) {
        $majorVersion = [int]$Matches[1]
        $minorVersion = [int]$Matches[2]
        if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
            Write-Host "  ⚠ 警告: Python 版本过低，建议升级到 3.8 或更高版本" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ✗ Python 未安装" -ForegroundColor Red
    Write-Host "    下载地址: https://www.python.org/downloads/" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 4. 检测 pip
# ===================================================================
Write-Host "[4/8] 检测 pip..." -ForegroundColor Yellow
if (Test-Command "pip") {
    $pipVersion = Get-Version "pip" "--version"
    Write-Host "  ✓ pip 已安装: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ pip 未安装" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 5. 检测 MySQL
# ===================================================================
Write-Host "[5/8] 检测 MySQL..." -ForegroundColor Yellow
if (Test-Command "mysql") {
    $mysqlVersion = Get-Version "mysql" "--version"
    Write-Host "  ✓ MySQL 客户端已安装: $mysqlVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠ MySQL 客户端未安装（可选）" -ForegroundColor Yellow
}

# 检测 MySQL 服务
$mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    Write-Host "  ✓ MySQL 服务已安装: $($mysqlService.DisplayName)" -ForegroundColor Green
    if ($mysqlService.Status -eq "Running") {
        Write-Host "    状态: 运行中" -ForegroundColor Green
    } else {
        Write-Host "    状态: 已停止" -ForegroundColor Yellow
        Write-Host "    启动命令: Start-Service $($mysqlService.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ MySQL 服务未安装" -ForegroundColor Red
    Write-Host "    下载地址: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 6. 检测 PM2
# ===================================================================
Write-Host "[6/8] 检测 PM2..." -ForegroundColor Yellow
if (Test-Command "pm2") {
    $pm2Version = Get-Version "pm2" "-v"
    Write-Host "  ✓ PM2 已安装: v$pm2Version" -ForegroundColor Green
} else {
    Write-Host "  ✗ PM2 未安装（生产环境必需）" -ForegroundColor Red
    Write-Host "    安装命令: npm install -g pm2" -ForegroundColor Gray
    Write-Host "    安装命令: npm install -g pm2-windows-startup" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 7. 检测 Git
# ===================================================================
Write-Host "[7/8] 检测 Git..." -ForegroundColor Yellow
if (Test-Command "git") {
    $gitVersion = Get-Version "git" "--version"
    Write-Host "  ✓ Git 已安装: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Git 未安装（可选，用于版本管理）" -ForegroundColor Yellow
    Write-Host "    下载地址: https://git-scm.com/download/win" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# 8. 检测防火墙和端口
# ===================================================================
Write-Host "[8/8] 检测防火墙和端口..." -ForegroundColor Yellow

# 检测端口 3000 是否被占用
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "  ⚠ 端口 3000 已被占用" -ForegroundColor Yellow
    Write-Host "    占用进程: PID $($port3000.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "  ✓ 端口 3000 可用" -ForegroundColor Green
}

# 检测端口 8765 是否被占用（WebSocket）
$port8765 = Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue
if ($port8765) {
    Write-Host "  ⚠ 端口 8765 已被占用" -ForegroundColor Yellow
    Write-Host "    占用进程: PID $($port8765.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "  ✓ 端口 8765 可用" -ForegroundColor Green
}

# 检测防火墙状态
$firewallProfile = Get-NetFirewallProfile -Profile Domain,Public,Private
$enabledProfiles = $firewallProfile | Where-Object { $_.Enabled -eq $true }
if ($enabledProfiles) {
    Write-Host "  ℹ 防火墙已启用，需要开放端口 3000 和 8765" -ForegroundColor Cyan
    Write-Host "    开放命令: New-NetFirewallRule -DisplayName 'Trading Dashboard' -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow" -ForegroundColor Gray
} else {
    Write-Host "  ⚠ 防火墙已禁用（不推荐）" -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 检测 Python 依赖
# ===================================================================
Write-Host "检测 Python 依赖..." -ForegroundColor Yellow
$pythonPackages = @("ccxt", "websocket-client", "requests", "pandas", "numpy")
$missingPackages = @()

foreach ($package in $pythonPackages) {
    try {
        $result = & pip show $package 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $package 已安装" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $package 未安装" -ForegroundColor Red
            $missingPackages += $package
        }
    } catch {
        Write-Host "  ✗ $package 未安装" -ForegroundColor Red
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "  缺失的 Python 包: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "  安装命令: pip install $($missingPackages -join ' ')" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 总结
# ===================================================================
Write-Host "========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "  ✓ 环境检测通过！" -ForegroundColor Green
    Write-Host "  您的服务器已准备好部署交易系统" -ForegroundColor Green
} else {
    Write-Host "  ✗ 环境检测未通过" -ForegroundColor Red
    Write-Host "  请根据上述提示安装缺失的依赖" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 暂停以便查看结果
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
