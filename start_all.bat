@echo off
title Trading Dashboard - Start Services

echo ========================================
echo   Trading Dashboard - Quick Start
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Recommend running as Administrator
    echo.
    timeout /t 3 >nul
)

REM Switch to project directory
cd /d "%~dp0"

echo [1/5] Checking PM2 installation...
where pm2 >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] PM2 is not installed
    echo Please run: npm install -g pm2
    pause
    exit /b 1
)
echo [OK] PM2 is installed
echo.

echo [2/5] Checking configuration file...
if not exist ".env" (
    echo [ERROR] .env file does not exist
    echo Please copy .env.example to .env and configure it
    pause
    exit /b 1
)
echo [OK] Configuration file exists
echo.

echo [3/5] Stopping old services...
pm2 delete all >nul 2>&1
echo [OK] Old services cleaned
echo.

echo [4/5] Starting services...
echo   - Web Dashboard (port 3000)
pm2 start ecosystem.config.js --only trading-dashboard
echo   - WebSocket Server (port 8765)
pm2 start ecosystem.config.js --only websocket-server
echo.

echo [5/5] Saving PM2 configuration...
pm2 save
echo [OK] Configuration saved
echo.

echo ========================================
echo   Services Started Successfully!
echo ========================================
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo Access URL: http://!IP!:3000
)
echo Access URL: http://localhost:3000
echo.

echo Common Commands:
echo   Check status: pm2 list
echo   View logs:    pm2 logs
echo   Restart:      pm2 restart all
echo   Stop:         pm2 stop all
echo.

echo Next Steps:
echo   1. Open the URL above in your browser
echo   2. Check if Dashboard displays correctly
echo   3. To start trading bot, run: start_trading_bot.bat
echo.

pause
