@echo off
chcp 65001 >nul
title 10U战神滚仓策略 - 停止服务

echo ========================================
echo   10U战神滚仓策略 - 停止服务
echo ========================================
echo.

REM 切换到项目目录
cd /d "%~dp0"

echo [警告] 即将停止所有服务
echo.

set /p confirm="确认停止所有服务? (输入 YES 继续): "
if /i not "%confirm%"=="YES" (
    echo 已取消操作
    pause
    exit /b 0
)

echo.
echo 停止所有服务...
pm2 stop all

echo.
echo ========================================
echo   所有服务已停止
echo ========================================
echo.

echo 查看服务状态:
pm2 list
echo.

echo 如需重新启动:
echo   启动所有服务: start_all.bat
echo   或使用命令: pm2 restart all
echo.

pause
