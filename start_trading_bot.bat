@echo off
title Trading Dashboard - Start Trading Bot

echo ========================================
echo   Trading Dashboard - Start Trading Bot
echo ========================================
echo.

REM Switch to project directory
cd /d "%~dp0"

echo [WARNING] About to start trading bot
echo.
echo Please confirm:
echo   1. KuCoin API keys are configured in .env
echo   2. Strategy parameters are tested
echo   3. Stop-loss and take-profit are set
echo   4. Account balance is sufficient
echo.

set /p confirm="Confirm to start trading bot? (Enter YES to continue): "
if /i not "%confirm%"=="YES" (
    echo Startup cancelled
    pause
    exit /b 0
)

echo.
echo [1/3] Checking PM2 installation...
where pm2 >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] PM2 is not installed
    echo Please run: npm install -g pm2
    pause
    exit /b 1
)
echo [OK] PM2 is installed
echo.

echo [2/3] Checking trading script...
if not exist "scripts\kucoin_api.py" (
    echo [ERROR] Trading script not found: scripts\kucoin_api.py
    pause
    exit /b 1
)
echo [OK] Trading script exists
echo.

echo [3/3] Starting trading bot...
pm2 start ecosystem.config.js --only trading-bot
if %errorLevel% neq 0 (
    echo [ERROR] Startup failed
    echo Please check logs: pm2 logs trading-bot
    pause
    exit /b 1
)
echo [OK] Trading bot started
echo.

echo Saving PM2 configuration...
pm2 save
echo.

echo ========================================
echo   Trading Bot Started Successfully!
echo ========================================
echo.

echo Common Commands:
echo   Check status:  pm2 list
echo   View logs:     pm2 logs trading-bot
echo   Stop bot:      pm2 stop trading-bot
echo   Restart bot:   pm2 restart trading-bot
echo.

echo Important Notes:
echo   - Monitor trading logs closely
echo   - Enable Telegram notifications
echo   - Check account balance and positions regularly
echo   - Stop immediately if abnormal: pm2 stop trading-bot
echo.

pause
