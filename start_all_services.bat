@echo off
echo ========================================
echo   Trading Dashboard - Start Services
echo ========================================
echo.

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

echo [2/4] Checking PM2 configuration...
if not exist "ecosystem.config.js" (
    echo [ERROR] ecosystem.config.js not found!
    echo Please ensure the configuration file exists
    pause
    exit /b 1
)
echo [OK] Configuration file exists
echo.

echo [3/4] Creating logs directory...
if not exist "logs" mkdir logs
echo [OK] Logs directory ready
echo.

echo [4/4] Starting all services...
pm2 start ecosystem.config.js
echo.

echo ========================================
echo   Service Status
echo ========================================
pm2 list
echo.

echo ========================================
echo   Services Started Successfully!
echo ========================================
echo.
echo To view logs: pm2 logs
echo To stop all: pm2 stop all
echo To restart: pm2 restart all
echo.

pause
