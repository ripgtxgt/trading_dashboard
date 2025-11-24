@echo off
chcp 65001 >nul
title 环境检测工具

echo ========================================
echo   10U战神滚仓策略 - 环境检测工具
echo ========================================
echo.
echo 正在启动环境检测脚本...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 运行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "scripts\check_windows_environment.ps1"

REM 如果PowerShell执行失败
if %errorLevel% neq 0 (
    echo.
    echo [错误] PowerShell脚本执行失败
    echo 请确保已安装PowerShell
    echo.
    pause
    exit /b 1
)

exit /b 0
