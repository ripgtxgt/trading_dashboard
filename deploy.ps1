<#
.SYNOPSIS
    Trading Dashboard 一键部署脚本 for Windows Server 2022
.DESCRIPTION
    自动检查环境、安装依赖、配置服务、启动应用
.NOTES
    版本: 1.0
    作者: Manus AI
    日期: 2025-11-26
#>

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

# 显示欢迎信息
function Show-Welcome {
    Clear-Host
    Write-ColorOutput @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║       Trading Dashboard 一键部署程序                      ║
║       Version 1.0 for Windows Server 2022                 ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ "Cyan"
    Write-Host ""
}

# 检查管理员权限
function Test-AdminPrivileges {
    Write-Info "检查管理员权限..."
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Error "需要管理员权限运行此脚本"
        Write-Warning "请右键点击 PowerShell 选择 '以管理员身份运行'"
        exit 1
    }
    Write-Success "管理员权限检查通过"
}

# 检查Python环境
function Test-Python {
    Write-Info "检查Python环境..."
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)") {
            $minorVersion = [int]$matches[1]
            if ($minorVersion -ge 11) {
                Write-Success "Python环境检查通过: $pythonVersion"
                return $true
            }
        }
        Write-Warning "Python版本过低，需要3.11或更高版本"
        return $false
    } catch {
        Write-Warning "未找到Python"
        return $false
    }
}

# 检查Node.js环境
function Test-NodeJS {
    Write-Info "检查Node.js环境..."
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v(\d+)") {
            $majorVersion = [int]$matches[1]
            if ($majorVersion -ge 20) {
                Write-Success "Node.js环境检查通过: $nodeVersion"
                return $true
            }
        }
        Write-Warning "Node.js版本过低，需要v20或更高版本"
        return $false
    } catch {
        Write-Warning "未找到Node.js"
        return $false
    }
}

# 检查pnpm
function Test-PNPM {
    Write-Info "检查pnpm..."
    try {
        $pnpmVersion = pnpm --version 2>&1
        Write-Success "pnpm已安装: v$pnpmVersion"
        return $true
    } catch {
        Write-Warning "未找到pnpm"
        return $false
    }
}

# 检查PM2
function Test-PM2 {
    Write-Info "检查PM2..."
    try {
        $pm2Version = pm2 --version 2>&1
        Write-Success "PM2已安装: v$pm2Version"
        return $true
    } catch {
        Write-Warning "未找到PM2"
        return $false
    }
}

# 检查MySQL
function Test-MySQL {
    Write-Info "检查MySQL..."
    try {
        $mysqlVersion = mysql --version 2>&1
        if ($mysqlVersion -match "mysql") {
            Write-Success "MySQL已安装"
            return $true
        }
        Write-Warning "未找到MySQL"
        return $false
    } catch {
        Write-Warning "未找到MySQL"
        return $false
    }
}

# 安装pnpm
function Install-PNPM {
    Write-Info "安装pnpm..."
    try {
        npm install -g pnpm
        Write-Success "pnpm安装成功"
    } catch {
        Write-Error "pnpm安装失败: $_"
        exit 1
    }
}

# 安装PM2
function Install-PM2 {
    Write-Info "安装PM2..."
    try {
        npm install -g pm2
        npm install -g pm2-windows-startup
        pm2-startup install
        Write-Success "PM2安装成功"
    } catch {
        Write-Error "PM2安装失败: $_"
        exit 1
    }
}

# 安装Node.js依赖
function Install-NodeDependencies {
    Write-Info "安装Node.js依赖（这可能需要几分钟）..."
    try {
        pnpm install
        Write-Success "Node.js依赖安装成功"
    } catch {
        Write-Error "Node.js依赖安装失败: $_"
        exit 1
    }
}

# 安装Python依赖
function Install-PythonDependencies {
    Write-Info "安装Python依赖..."
    try {
        if (Test-Path "requirements.txt") {
            pip install -r requirements.txt
            Write-Success "Python依赖安装成功"
        } else {
            Write-Warning "未找到requirements.txt"
        }
    } catch {
        Write-Error "Python依赖安装失败: $_"
        exit 1
    }
}

# 配置环境变量
function Set-EnvironmentConfig {
    Write-Info "配置环境变量..."
    
    if (Test-Path ".env") {
        Write-Warning ".env文件已存在，是否覆盖？(y/n)"
        $overwrite = Read-Host
        if ($overwrite -ne "y") {
            Write-Info "跳过环境变量配置"
            return
        }
    }
    
    Write-Host ""
    Write-ColorOutput "请输入配置信息（直接回车使用默认值）：" "Yellow"
    Write-Host ""
    
    # KuCoin配置
    Write-ColorOutput "=== KuCoin API配置 ===" "Cyan"
    $apiKey = Read-Host "API Key"
    $apiSecret = Read-Host "API Secret"
    $apiPassphrase = Read-Host "API Passphrase"
    $sandbox = Read-Host "使用沙盒环境？(true/false) [默认: false]"
    if ([string]::IsNullOrWhiteSpace($sandbox)) { $sandbox = "false" }
    
    # 数据库配置
    Write-Host ""
    Write-ColorOutput "=== 数据库配置 ===" "Cyan"
    $dbHost = Read-Host "数据库主机 [默认: localhost]"
    if ([string]::IsNullOrWhiteSpace($dbHost)) { $dbHost = "localhost" }
    $dbPort = Read-Host "数据库端口 [默认: 3306]"
    if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "3306" }
    $dbUser = Read-Host "数据库用户名 [默认: trading]"
    if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "trading" }
    $dbPassword = Read-Host "数据库密码"
    $dbName = Read-Host "数据库名称 [默认: trading_dashboard]"
    if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "trading_dashboard" }
    
    # Telegram配置
    Write-Host ""
    Write-ColorOutput "=== Telegram配置 ===" "Cyan"
    $telegramToken = Read-Host "Bot Token"
    $telegramChatId = Read-Host "Chat ID"
    
    # 交易配置
    Write-Host ""
    Write-ColorOutput "=== 交易配置 ===" "Cyan"
    $leverage = Read-Host "杠杆倍数 [默认: 100]"
    if ([string]::IsNullOrWhiteSpace($leverage)) { $leverage = "100" }
    $initialCapital = Read-Host "初始资金 [默认: 10]"
    if ([string]::IsNullOrWhiteSpace($initialCapital)) { $initialCapital = "10" }
    
    # 写入.env文件
    $envContent = @"
# KuCoin API配置
KUCOIN_API_KEY=$apiKey
KUCOIN_API_SECRET=$apiSecret
KUCOIN_API_PASSPHRASE=$apiPassphrase
KUCOIN_SANDBOX=$sandbox

# 数据库配置
DB_HOST=$dbHost
DB_PORT=$dbPort
DB_USER=$dbUser
DB_PASSWORD=$dbPassword
DB_NAME=$dbName

# Telegram配置
TELEGRAM_BOT_TOKEN=$telegramToken
TELEGRAM_CHAT_ID=$telegramChatId

# 交易配置
LEVERAGE=$leverage
INITIAL_CAPITAL=$initialCapital

# 生成时间
# Generated at: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline
    Write-Success "环境变量配置完成"
}

# 初始化数据库
function Initialize-Database {
    Write-Info "初始化数据库..."
    
    if (-not (Test-Path "database/schema.sql")) {
        Write-Warning "未找到数据库schema文件，跳过初始化"
        return
    }
    
    Write-Warning "是否初始化数据库？这将创建新的表结构 (y/n)"
    $confirm = Read-Host
    if ($confirm -ne "y") {
        Write-Info "跳过数据库初始化"
        return
    }
    
    try {
        # 读取.env获取数据库配置
        $env = Get-Content ".env" | ConvertFrom-StringData
        $dbUser = $env.DB_USER
        $dbPassword = $env.DB_PASSWORD
        $dbName = $env.DB_NAME
        
        # 执行SQL
        Get-Content "database\schema.sql" | mysql -u $dbUser -p$dbPassword $dbName
        Write-Success "数据库初始化成功"
    } catch {
        Write-Error "数据库初始化失败: $_"
        Write-Warning "请手动执行: mysql -u root -p < database/schema.sql"
    }
}

# 启动服务
function Start-Services {
    Write-Info "启动服务..."
    
    try {
        # 停止旧的服务
        pm2 delete all 2>$null
        
        # 启动新服务
        pm2 start ecosystem.config.cjs
        pm2 save
        
        Write-Success "服务启动成功"
        Write-Host ""
        Write-ColorOutput "服务状态：" "Yellow"
        pm2 list
    } catch {
        Write-Error "服务启动失败: $_"
        exit 1
    }
}

# 显示完成信息
function Show-Completion {
    Write-Host ""
    Write-ColorOutput @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                  部署完成！                                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ "Green"
    
    Write-Host ""
    Write-ColorOutput "下一步操作：" "Yellow"
    Write-Host ""
    Write-Host "  1. 查看服务状态：pm2 list"
    Write-Host "  2. 查看日志：pm2 logs"
    Write-Host "  3. 访问Dashboard：http://localhost:3000"
    Write-Host ""
    Write-ColorOutput "常用命令：" "Yellow"
    Write-Host ""
    Write-Host "  pm2 restart all     - 重启所有服务"
    Write-Host "  pm2 stop all        - 停止所有服务"
    Write-Host "  pm2 logs            - 查看所有日志"
    Write-Host "  pm2 monit           - 监控服务"
    Write-Host ""
}

# 主函数
function Main {
    Show-Welcome
    
    # 检查管理员权限
    Test-AdminPrivileges
    
    Write-Host ""
    Write-ColorOutput "=== 环境检查 ===" "Yellow"
    Write-Host ""
    
    # 检查必需环境
    $pythonOK = Test-Python
    $nodeOK = Test-NodeJS
    $pnpmOK = Test-PNPM
    $pm2OK = Test-PM2
    $mysqlOK = Test-MySQL
    
    # 如果缺少必需环境，提示用户
    if (-not $pythonOK) {
        Write-Error "请先安装Python 3.11或更高版本"
        Write-Info "下载地址: https://www.python.org/downloads/"
        exit 1
    }
    
    if (-not $nodeOK) {
        Write-Error "请先安装Node.js 20或更高版本"
        Write-Info "下载地址: https://nodejs.org/"
        exit 1
    }
    
    if (-not $mysqlOK) {
        Write-Warning "未检测到MySQL，请确保已安装MySQL 8.0或更高版本"
        Write-Info "下载地址: https://dev.mysql.com/downloads/mysql/"
    }
    
    # 安装可选组件
    if (-not $pnpmOK) {
        Install-PNPM
    }
    
    if (-not $pm2OK) {
        Install-PM2
    }
    
    Write-Host ""
    Write-ColorOutput "=== 安装依赖 ===" "Yellow"
    Write-Host ""
    
    # 安装依赖
    Install-NodeDependencies
    Install-PythonDependencies
    
    Write-Host ""
    Write-ColorOutput "=== 配置应用 ===" "Yellow"
    Write-Host ""
    
    # 配置环境变量
    Set-EnvironmentConfig
    
    # 初始化数据库
    Initialize-Database
    
    Write-Host ""
    Write-ColorOutput "=== 启动服务 ===" "Yellow"
    Write-Host ""
    
    # 启动服务
    Start-Services
    
    # 显示完成信息
    Show-Completion
}

# 运行主函数
try {
    Main
} catch {
    Write-Error "部署过程中发生错误: $_"
    Write-Host ""
    Write-Warning "请查看错误信息并重试，或参考文档手动部署"
    exit 1
}
