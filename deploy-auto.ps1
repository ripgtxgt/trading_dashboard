<#
.SYNOPSIS
    Trading Dashboard 自动部署脚本（用于GitHub Actions）
.DESCRIPTION
    自动安装依赖、构建项目、复制文件、重启服务
.NOTES
    版本: 2.0
    作者: Manus AI
    日期: 2025-11-26
#>

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message); Write-ColorOutput "✓ $Message" "Green" }
function Write-Error { param([string]$Message); Write-ColorOutput "✗ $Message" "Red" }
function Write-Info { param([string]$Message); Write-ColorOutput "ℹ $Message" "Cyan" }

Write-Info "开始自动部署..."

try {
    # 1. 安装Node.js依赖
    Write-Info "安装Node.js依赖..."
    pnpm install
    Write-Success "依赖安装完成"
    
    # 2. 安装Python依赖
    Write-Info "安装Python依赖..."
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt -q
        Write-Success "Python依赖安装完成"
    }
    
    # 3. 构建前端
    Write-Info "构建前端..."
    pnpm run build
    Write-Success "前端构建完成"
    
    # 4. 复制构建文件到正确位置
    Write-Info "复制构建文件..."
    if (Test-Path "dist\public") {
        New-Item -ItemType Directory -Force -Path "server\_core\public" | Out-Null
        Copy-Item -Path "dist\public\*" -Destination "server\_core\public\" -Recurse -Force
        Write-Success "构建文件复制完成"
    }
    
    # 5. 数据库迁移（如果需要）
    Write-Info "检查数据库迁移..."
    if (Test-Path "drizzle") {
        pnpm drizzle-kit push
        Write-Success "数据库迁移完成"
    }
    
    # 6. 重启PM2服务
    Write-Info "Restarting services..."
    
    # Stop all services first
    pm2 stop all
    
    # Delete old processes
    pm2 delete all
    
    # Start with ecosystem config
    pm2 start ecosystem.config.cjs
    
    # Save PM2 process list
    pm2 save
    
    Write-Success "Services restarted successfully"
    
    # 7. 等待服务启动
    Write-Info "等待服务启动..."
    Start-Sleep -Seconds 5
    
    # 8. 检查服务状态
    Write-Info "检查服务状态..."
    $status = pm2 list
    Write-Host $status
    
    Write-Success "部署完成！"
    
} catch {
    Write-Error "部署失败: $_"
    exit 1
}
