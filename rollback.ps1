# 一键回滚脚本
# 用途：快速回滚到上一个稳定版本

param(
    [string]$Version = "HEAD~1",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProjectPath = "C:\trading_dashboard_fixed"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trading Dashboard - 一键回滚工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到项目目录
Set-Location $ProjectPath

# 显示当前版本
Write-Host "当前版本信息：" -ForegroundColor Yellow
git log -1 --oneline
Write-Host ""

# 显示回滚目标版本
Write-Host "回滚目标版本：" -ForegroundColor Yellow
git log $Version -1 --oneline
Write-Host ""

# 确认回滚
if (-not $Force) {
    $confirm = Read-Host "确认回滚到此版本？(y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "回滚已取消" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "开始回滚..." -ForegroundColor Green

try {
    # 1. 保存当前状态（以防需要恢复）
    Write-Host "[1/6] 保存当前状态..." -ForegroundColor Cyan
    $currentCommit = git rev-parse HEAD
    Write-Host "  当前提交: $currentCommit" -ForegroundColor Gray
    
    # 2. 停止所有服务
    Write-Host "[2/6] 停止所有服务..." -ForegroundColor Cyan
    pm2 stop all
    Start-Sleep -Seconds 3
    
    # 3. 回滚代码
    Write-Host "[3/6] 回滚代码..." -ForegroundColor Cyan
    git reset --hard $Version
    
    # 4. 安装依赖
    Write-Host "[4/6] 安装依赖..." -ForegroundColor Cyan
    pnpm install
    
    # 5. 构建项目
    Write-Host "[5/6] 构建项目..." -ForegroundColor Cyan
    pnpm build
    
    # 复制构建文件
    Write-Host "  复制构建文件..." -ForegroundColor Gray
    if (Test-Path "dist/public") {
        Copy-Item -Path "dist/public/*" -Destination "server/_core/public" -Recurse -Force
        Write-Host "  ✓ 构建文件已复制" -ForegroundColor Green
    }
    
    # 6. 重启所有服务
    Write-Host "[6/6] 重启所有服务..." -ForegroundColor Cyan
    pm2 restart all
    Start-Sleep -Seconds 5
    
    # 显示服务状态
    Write-Host ""
    Write-Host "服务状态：" -ForegroundColor Yellow
    pm2 list
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ 回滚成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "回滚信息：" -ForegroundColor Yellow
    Write-Host "  原版本: $currentCommit" -ForegroundColor Gray
    Write-Host "  新版本: $(git rev-parse HEAD)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "如需恢复到回滚前的版本，请执行：" -ForegroundColor Yellow
    Write-Host "  .\rollback.ps1 -Version $currentCommit -Force" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ 回滚失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "错误信息：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "建议操作：" -ForegroundColor Yellow
    Write-Host "  1. 检查错误日志" -ForegroundColor Gray
    Write-Host "  2. 手动恢复：git reset --hard $currentCommit" -ForegroundColor Gray
    Write-Host "  3. 重启服务：pm2 restart all" -ForegroundColor Gray
    
    exit 1
}
