@echo off
chcp 65001 > nul
echo ========================================
echo   Trading Dashboard - Start Services
echo ========================================
echo.

REM 检查PM2是否安装
echo [1/4] Checking PM2 installation...
where pm2 > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PM2 is not installed!
    echo Please install PM2: npm install -g pm2
    pause
    exit /b 1
)
echo [OK] PM2 is installed
echo.

REM 检查ecosystem.config.js是否存在
echo [2/4] Checking PM2 configuration...
if not exist "ecosystem.config.js" (
    echo [ERROR] ecosystem.config.js not found!
    echo Please ensure the configuration file exists
    pause
    exit /b 1
)
echo [OK] Configuration file exists
echo.

REM 创建logs目录
echo [3/4] Creating logs directory...
if not exist "logs" mkdir logs
echo [OK] Logs directory ready
echo.

REM 启动所有服务
echo [4/4] Starting all services...
pm2 start ecosystem.config.js
echo.

REM 显示服务状态
echo ========================================
echo   Service Status
echo ========================================
pm2 list
echo.

echo ========================================
echo   Services Started Successfully!
echo ========================================
echo.
echo To view logs:
echo   pm2 logs trading-dashboard
echo   pm2 logs trading-bot
echo   pm2 logs telegram-bot
echo   pm2 logs websocket-server
echo   pm2 logs daily-report
echo.
echo To stop all services:
echo   pm2 stop all
echo.
echo To restart all services:
echo   pm2 restart all
echo.

pause
