# ===================================================================
# Windows Server 自动化部署脚本
# 用途：自动部署10U战神滚仓策略交易系统到Windows服务器
# ===================================================================

param(
    [string]$ProjectPath = "C:\trading_dashboard",
    [switch]$SkipBuild = $false,
    [switch]$SkipDB = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  10U战神滚仓策略 - 自动化部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# ===================================================================
# 1. 检查项目路径
# ===================================================================
Write-Host "[1/10] 检查项目路径..." -ForegroundColor Yellow
if (-not (Test-Path $ProjectPath)) {
    Write-Host "  ✗ 项目路径不存在: $ProjectPath" -ForegroundColor Red
    Write-Host "  请先将项目文件复制到服务器" -ForegroundColor Yellow
    exit 1
}
Write-Host "  ✓ 项目路径存在: $ProjectPath" -ForegroundColor Green
Set-Location $ProjectPath
Write-Host ""

# ===================================================================
# 2. 检查 .env 文件
# ===================================================================
Write-Host "[2/10] 检查环境变量配置..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "  ⚠ .env 文件不存在，从 .env.example 复制..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ 已创建 .env 文件" -ForegroundColor Green
        Write-Host "  ⚠ 请编辑 .env 文件，填入正确的配置信息" -ForegroundColor Yellow
        Write-Host "  配置文件路径: $ProjectPath\.env" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  按任意键继续..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "  ✗ .env 和 .env.example 文件都不存在" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✓ .env 文件已存在" -ForegroundColor Green
}
Write-Host ""

# ===================================================================
# 3. 安装 Node.js 依赖
# ===================================================================
Write-Host "[3/10] 安装 Node.js 依赖..." -ForegroundColor Yellow
if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
    Write-Host "  使用 pnpm 安装依赖..." -ForegroundColor Cyan
    pnpm install
} else {
    Write-Host "  使用 npm 安装依赖..." -ForegroundColor Cyan
    npm install
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ 依赖安装失败" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Node.js 依赖安装完成" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 4. 安装 Python 依赖
# ===================================================================
Write-Host "[4/10] 安装 Python 依赖..." -ForegroundColor Yellow
if (Test-Path "scripts\requirements.txt") {
    pip install -r scripts\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Python 依赖安装失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Python 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "  ⚠ requirements.txt 不存在，跳过 Python 依赖安装" -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 5. 数据库迁移
# ===================================================================
if (-not $SkipDB) {
    Write-Host "[5/10] 执行数据库迁移..." -ForegroundColor Yellow
    try {
        if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
            pnpm db:push
        } else {
            npm run db:push
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ✗ 数据库迁移失败" -ForegroundColor Red
            Write-Host "  请检查 DATABASE_URL 配置是否正确" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "  ✓ 数据库迁移完成" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ 数据库迁移失败: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[5/10] 跳过数据库迁移..." -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 6. 构建前端
# ===================================================================
if (-not $SkipBuild) {
    Write-Host "[6/10] 构建前端..." -ForegroundColor Yellow
    try {
        if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
            pnpm build
        } else {
            npm run build
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ✗ 前端构建失败" -ForegroundColor Red
            exit 1
        }
        Write-Host "  ✓ 前端构建完成" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ 前端构建失败: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[6/10] 跳过前端构建..." -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 7. 配置 PM2
# ===================================================================
Write-Host "[7/10] 配置 PM2..." -ForegroundColor Yellow
if (-not (Get-Command "pm2" -ErrorAction SilentlyContinue)) {
    Write-Host "  ✗ PM2 未安装" -ForegroundColor Red
    Write-Host "  安装命令: npm install -g pm2" -ForegroundColor Gray
    exit 1
}

# 停止旧的进程
Write-Host "  停止旧的进程..." -ForegroundColor Cyan
pm2 delete trading-dashboard 2>$null
pm2 delete trading-bot 2>$null
pm2 delete websocket-server 2>$null

Write-Host "  ✓ PM2 配置完成" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 8. 启动服务
# ===================================================================
Write-Host "[8/10] 启动服务..." -ForegroundColor Yellow

# 启动 Web Dashboard
Write-Host "  启动 Web Dashboard..." -ForegroundColor Cyan
if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
    pm2 start pnpm --name "trading-dashboard" -- start
} else {
    pm2 start npm --name "trading-dashboard" -- start
}

# 启动 WebSocket 服务器
Write-Host "  启动 WebSocket 服务器..." -ForegroundColor Cyan
pm2 start python --name "websocket-server" -- scripts/websocket_pusher.py

# 启动交易机器人（可选）
Write-Host "  ℹ 交易机器人需要手动启动" -ForegroundColor Cyan
Write-Host "    启动命令: pm2 start python --name trading-bot -- scripts/kucoin_api.py" -ForegroundColor Gray

Write-Host "  ✓ 服务启动完成" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 9. 保存 PM2 配置
# ===================================================================
Write-Host "[9/10] 保存 PM2 配置..." -ForegroundColor Yellow
pm2 save
Write-Host "  ✓ PM2 配置已保存" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 10. 配置开机自启
# ===================================================================
Write-Host "[10/10] 配置开机自启..." -ForegroundColor Yellow
if (Get-Command "pm2-startup" -ErrorAction SilentlyContinue) {
    Write-Host "  配置 PM2 开机自启..." -ForegroundColor Cyan
    pm2-startup install
    Write-Host "  ✓ 开机自启配置完成" -ForegroundColor Green
} else {
    Write-Host "  ⚠ pm2-startup 未安装" -ForegroundColor Yellow
    Write-Host "    安装命令: npm install -g pm2-windows-startup" -ForegroundColor Gray
    Write-Host "    配置命令: pm2-startup install" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# 配置防火墙
# ===================================================================
Write-Host "配置防火墙..." -ForegroundColor Yellow
try {
    # 检查防火墙规则是否已存在
    $existingRule = Get-NetFirewallRule -DisplayName "Trading Dashboard" -ErrorAction SilentlyContinue
    if ($existingRule) {
        Write-Host "  ℹ 防火墙规则已存在" -ForegroundColor Cyan
    } else {
        Write-Host "  添加防火墙规则..." -ForegroundColor Cyan
        New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow
        Write-Host "  ✓ 防火墙规则添加成功" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ 防火墙配置失败（可能需要管理员权限）" -ForegroundColor Yellow
    Write-Host "    手动配置命令: New-NetFirewallRule -DisplayName 'Trading Dashboard' -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# 显示服务状态
# ===================================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服务状态" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
pm2 list
Write-Host ""

# ===================================================================
# 显示访问信息
# ===================================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Yellow

# 获取本机 IP 地址
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }
foreach ($ip in $ipAddresses) {
    Write-Host "  http://$($ip.IPAddress):3000" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "常用命令:" -ForegroundColor Yellow
Write-Host "  查看服务状态:    pm2 list" -ForegroundColor Gray
Write-Host "  查看日志:        pm2 logs" -ForegroundColor Gray
Write-Host "  重启服务:        pm2 restart all" -ForegroundColor Gray
Write-Host "  停止服务:        pm2 stop all" -ForegroundColor Gray
Write-Host "  启动交易机器人:  pm2 start python --name trading-bot -- scripts/kucoin_api.py" -ForegroundColor Gray
Write-Host ""

Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 在浏览器中访问上述地址" -ForegroundColor Gray
Write-Host "  2. 检查 .env 配置是否正确" -ForegroundColor Gray
Write-Host "  3. 配置 KuCoin API 密钥" -ForegroundColor Gray
Write-Host "  4. 配置 Telegram Bot Token" -ForegroundColor Gray
Write-Host "  5. 启动交易机器人" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
