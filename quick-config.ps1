<#
.SYNOPSIS
    快速配置向导
.DESCRIPTION
    交互式配置环境变量，无需手动编辑.env文件
#>

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

Clear-Host
Write-ColorOutput @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              Trading Dashboard 快速配置向导                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ "Cyan"

Write-Host ""
Write-ColorOutput "此向导将帮助您配置Trading Dashboard" "Yellow"
Write-Host ""

# 检查是否已有配置
if (Test-Path ".env") {
    Write-ColorOutput "检测到已存在的配置文件 .env" "Yellow"
    $overwrite = Read-Host "是否覆盖现有配置？(y/n)"
    if ($overwrite -ne "y") {
        Write-ColorOutput "配置已取消" "Red"
        exit 0
    }
}

Write-Host ""
Write-ColorOutput "请按提示输入配置信息（按回车使用默认值）" "Cyan"
Write-Host ""

# KuCoin配置
Write-ColorOutput "═══ 1/4 KuCoin API配置 ═══" "Green"
Write-Host ""
$apiKey = Read-Host "API Key (必填)"
while ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-ColorOutput "API Key不能为空" "Red"
    $apiKey = Read-Host "API Key (必填)"
}

$apiSecret = Read-Host "API Secret (必填)"
while ([string]::IsNullOrWhiteSpace($apiSecret)) {
    Write-ColorOutput "API Secret不能为空" "Red"
    $apiSecret = Read-Host "API Secret (必填)"
}

$apiPassphrase = Read-Host "API Passphrase (必填)"
while ([string]::IsNullOrWhiteSpace($apiPassphrase)) {
    Write-ColorOutput "API Passphrase不能为空" "Red"
    $apiPassphrase = Read-Host "API Passphrase (必填)"
}

$sandbox = Read-Host "使用沙盒环境？(true/false) [默认: false]"
if ([string]::IsNullOrWhiteSpace($sandbox)) { $sandbox = "false" }

# 数据库配置
Write-Host ""
Write-ColorOutput "═══ 2/4 数据库配置 ═══" "Green"
Write-Host ""
$dbHost = Read-Host "数据库主机 [默认: localhost]"
if ([string]::IsNullOrWhiteSpace($dbHost)) { $dbHost = "localhost" }

$dbPort = Read-Host "数据库端口 [默认: 3306]"
if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "3306" }

$dbUser = Read-Host "数据库用户名 [默认: trading]"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "trading" }

$dbPassword = Read-Host "数据库密码 (必填)"
while ([string]::IsNullOrWhiteSpace($dbPassword)) {
    Write-ColorOutput "数据库密码不能为空" "Red"
    $dbPassword = Read-Host "数据库密码 (必填)"
}

$dbName = Read-Host "数据库名称 [默认: trading_dashboard]"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "trading_dashboard" }

# Telegram配置
Write-Host ""
Write-ColorOutput "═══ 3/4 Telegram配置 ═══" "Green"
Write-Host ""
$telegramToken = Read-Host "Bot Token (必填)"
while ([string]::IsNullOrWhiteSpace($telegramToken)) {
    Write-ColorOutput "Bot Token不能为空" "Red"
    $telegramToken = Read-Host "Bot Token (必填)"
}

$telegramChatId = Read-Host "Chat ID (必填)"
while ([string]::IsNullOrWhiteSpace($telegramChatId)) {
    Write-ColorOutput "Chat ID不能为空" "Red"
    $telegramChatId = Read-Host "Chat ID (必填)"
}

# 交易配置
Write-Host ""
Write-ColorOutput "═══ 4/4 交易配置 ═══" "Green"
Write-Host ""
$leverage = Read-Host "杠杆倍数 [默认: 100]"
if ([string]::IsNullOrWhiteSpace($leverage)) { $leverage = "100" }

$initialCapital = Read-Host "初始资金(USDT) [默认: 10]"
if ([string]::IsNullOrWhiteSpace($initialCapital)) { $initialCapital = "10" }

# 确认配置
Write-Host ""
Write-ColorOutput "═══ 配置预览 ═══" "Yellow"
Write-Host ""
Write-Host "KuCoin API Key: $apiKey"
Write-Host "KuCoin Sandbox: $sandbox"
Write-Host "数据库: $dbUser@$dbHost:$dbPort/$dbName"
Write-Host "Telegram Bot: $telegramToken"
Write-Host "Telegram Chat ID: $telegramChatId"
Write-Host "杠杆倍数: ${leverage}x"
Write-Host "初始资金: ${initialCapital} USDT"
Write-Host ""

$confirm = Read-Host "确认以上配置？(y/n)"
if ($confirm -ne "y") {
    Write-ColorOutput "配置已取消" "Red"
    exit 0
}

# 生成.env文件
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

# 配置生成时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

try {
    $envContent | Out-File -FilePath ".env" -Encoding UTF8 -Force
    Write-Host ""
    Write-ColorOutput "✓ 配置文件已保存到 .env" "Green"
    Write-Host ""
    Write-ColorOutput "下一步：运行 DEPLOY.bat 开始部署" "Cyan"
} catch {
    Write-ColorOutput "✗ 保存配置文件失败: $_" "Red"
    exit 1
}

Write-Host ""
pause
