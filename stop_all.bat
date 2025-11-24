@echo off
title Trading Dashboard - Stop Services

echo ========================================
echo   Trading Dashboard - Stop Services
echo ========================================
echo.

REM Switch to project directory
cd /d "%~dp0"

echo [WARNING] About to stop all services
echo.

set /p confirm="Confirm to stop all services? (Enter YES to continue): "
if /i not "%confirm%"=="YES" (
    echo Operation cancelled
    pause
    exit /b 0
)

echo.
echo Stopping all services...
pm2 stop all

echo.
echo ========================================
echo   All Services Stopped
echo ========================================
echo.

echo Service Status:
pm2 list
echo.

echo To restart services:
echo   Start all services: start_all.bat
echo   Or use command:     pm2 restart all
echo.

pause
