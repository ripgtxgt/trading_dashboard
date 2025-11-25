@echo off
REM SSL Certificate Setup Wrapper
REM Runs the PowerShell script with proper execution policy

echo ========================================
echo SSL Certificate Setup
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [INFO] Starting SSL certificate setup...
echo.

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0setup_ssl_windows.ps1"

echo.
echo [INFO] SSL setup script completed
pause
