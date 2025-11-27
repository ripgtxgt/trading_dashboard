<#
.SYNOPSIS
    环境检查工具
.DESCRIPTION
    检查系统环境是否满足Trading Dashboard的运行要求
#>

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Component {
    param(
        [string]$Name,
        [scriptblock]$TestScript,
        [string]$MinVersion = "",
        [string]$DownloadUrl = ""
    )
    
    Write-Host -NoNewline "检查 $Name... "
    
    try {
        $result = & $TestScript
        if ($result.Success) {
            Write-ColorOutput "✓ 已安装 ($($result.Version))" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ 未安装或版本过低" "Red"
            if ($MinVersion) {
                Write-ColorOutput "  需要版本: $MinVersion" "Yellow"
            }
            if ($DownloadUrl) {
                Write-ColorOutput "  下载地址: $DownloadUrl" "Cyan"
            }
            return $false
        }
    } catch {
        Write-ColorOutput "✗ 检查失败" "Red"
        return $false
    }
}

Clear-Host
Write-ColorOutput @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              Trading Dashboard 环境检查工具                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ "Cyan"

Write-Host ""
Write-ColorOutput "正在检查系统环境..." "Yellow"
Write-Host ""

$allPassed = $true

# 检查Windows版本
$allPassed = (Test-Component "Windows版本" {
    $os = Get-CimInstance Win32_OperatingSystem
    $version = $os.Caption
    if ($version -match "Windows (Server|10|11)") {
        return @{ Success = $true; Version = $version }
    }
    return @{ Success = $false; Version = $version }
}) -and $allPassed

# 检查Python
$allPassed = (Test-Component "Python" {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)\.(\d+)") {
        $minor = [int]$matches[1]
        if ($minor -ge 11) {
            return @{ Success = $true; Version = $pythonVersion }
        }
    }
    return @{ Success = $false; Version = $pythonVersion }
} -MinVersion "3.11+" -DownloadUrl "https://www.python.org/downloads/") -and $allPassed

# 检查Node.js
$allPassed = (Test-Component "Node.js" {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(\d+)\.") {
        $major = [int]$matches[1]
        if ($major -ge 20) {
            return @{ Success = $true; Version = $nodeVersion }
        }
    }
    return @{ Success = $false; Version = $nodeVersion }
} -MinVersion "v20+" -DownloadUrl "https://nodejs.org/") -and $allPassed

# 检查npm
$allPassed = (Test-Component "npm" {
    $npmVersion = npm --version 2>&1
    if ($npmVersion -match "\d+\.\d+\.\d+") {
        return @{ Success = $true; Version = "v$npmVersion" }
    }
    return @{ Success = $false; Version = "" }
}) -and $allPassed

# 检查pnpm
Test-Component "pnpm" {
    $pnpmVersion = pnpm --version 2>&1
    if ($pnpmVersion -match "\d+\.\d+\.\d+") {
        return @{ Success = $true; Version = "v$pnpmVersion" }
    }
    return @{ Success = $false; Version = "" }
} -DownloadUrl "npm install -g pnpm" | Out-Null

# 检查PM2
Test-Component "PM2" {
    $pm2Version = pm2 --version 2>&1
    if ($pm2Version -match "\d+\.\d+\.\d+") {
        return @{ Success = $true; Version = "v$pm2Version" }
    }
    return @{ Success = $false; Version = "" }
} -DownloadUrl "npm install -g pm2" | Out-Null

# 检查MySQL
$allPassed = (Test-Component "MySQL" {
    $mysqlVersion = mysql --version 2>&1
    if ($mysqlVersion -match "mysql.*Ver (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        return @{ Success = $true; Version = "v$version" }
    }
    return @{ Success = $false; Version = "" }
} -MinVersion "8.0+" -DownloadUrl "https://dev.mysql.com/downloads/mysql/") -and $allPassed

# 检查Git (可选)
Test-Component "Git" {
    $gitVersion = git --version 2>&1
    if ($gitVersion -match "git version (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        return @{ Success = $true; Version = "v$version" }
    }
    return @{ Success = $false; Version = "" }
} -DownloadUrl "https://git-scm.com/download/win" | Out-Null

Write-Host ""
Write-ColorOutput "═══ 检查结果 ═══" "Yellow"
Write-Host ""

if ($allPassed) {
    Write-ColorOutput "✓ 所有必需组件已安装，可以开始部署！" "Green"
    Write-Host ""
    Write-ColorOutput "下一步：" "Cyan"
    Write-Host "  1. 运行 quick-config.ps1 配置环境变量"
    Write-Host "  2. 运行 DEPLOY.bat 开始部署"
} else {
    Write-ColorOutput "✗ 部分必需组件未安装或版本不符合要求" "Red"
    Write-Host ""
    Write-ColorOutput "请先安装缺失的组件，然后重新运行此检查" "Yellow"
}

Write-Host ""
Write-ColorOutput "可选组件（pnpm, PM2, Git）可以在部署时自动安装" "Cyan"
Write-Host ""

pause
