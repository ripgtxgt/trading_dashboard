@echo off
REM ========================================
REM Trading Dashboard Manual Deployment Script
REM ========================================
REM This script manually pulls latest code and deploys
REM Run this on Windows Server if GitHub Actions fails
REM ========================================

echo.
echo ========================================
echo Trading Dashboard Manual Deployment
echo ========================================
echo.

cd /d C:\trading_dashboard_fixed

echo [INFO] Pulling latest code from GitHub...
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull code from GitHub
    echo Please check your internet connection and Git configuration
    pause
    exit /b 1
)
echo [SUCCESS] Code pulled successfully
echo.

echo [INFO] Running deployment script...
powershell.exe -ExecutionPolicy Bypass -File .\deploy-auto.ps1

echo.
echo ========================================
echo Deployment completed!
echo ========================================
echo.
echo Next steps:
echo 1. Check service status: pm2 list
echo 2. View logs: pm2 logs
echo 3. Access dashboard: http://localhost:3000
echo.

pause
