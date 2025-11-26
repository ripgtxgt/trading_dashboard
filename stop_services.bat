@echo off
chcp 65001 > nul
echo ========================================
echo   Trading Dashboard - Stop Services
echo ========================================
echo.

REM 检查PM2是否安装
where pm2 > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PM2 is not installed!
    pause
    exit /b 1
)

REM 停止所有服务
echo Stopping all services...
pm2 stop all
echo.

REM 显示服务状态
echo ========================================
echo   Service Status
echo ========================================
pm2 list
echo.

echo ========================================
echo   All Services Stopped
echo ========================================
echo.

pause
