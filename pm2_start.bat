@echo off
echo ========================================
echo   Starting Trading Dashboard Services
echo ========================================
echo.

cd /d C:\trading_dashboard

echo Creating logs directory...
if not exist "logs" mkdir logs
echo.

echo Starting all services with PM2...
pm2 start ecosystem.config.cjs

echo.
echo ========================================
echo   Service Status
echo ========================================
pm2 list

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo.
echo View logs: pm2 logs
echo Stop all: pm2 stop all
echo Restart: pm2 restart all
echo.
echo Dashboard URL: http://localhost:3000
echo.

pause
