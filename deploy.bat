@echo off
chcp 65001 >nul
title 自动化部署工具

echo ========================================
echo   10U战神滚仓策略 - 自动化部署
echo ========================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [警告] 建议以管理员身份运行此脚本
    echo.
    echo 右键点击此文件，选择"以管理员身份运行"
    echo.
    set /p continue="是否继续? (输入 Y 继续): "
    if /i not "%continue%"=="Y" (
        echo 已取消部署
        pause
        exit /b 0
    )
)

echo.
echo 正在启动自动化部署脚本...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 运行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "scripts\deploy_windows.ps1"

REM 如果PowerShell执行失败
if %errorLevel% neq 0 (
    echo.
    echo [错误] 部署脚本执行失败
    echo 请查看上方错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.

pause
exit /b 0
