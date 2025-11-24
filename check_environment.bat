@echo off
title Environment Check Tool

echo ========================================
echo   Trading Dashboard - Environment Check
echo ========================================
echo.
echo Starting environment detection...
echo.

REM Switch to script directory
cd /d "%~dp0"

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "scripts\check_windows_environment.ps1"

REM Check if PowerShell execution failed
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] PowerShell script execution failed
    echo Please ensure PowerShell is installed
    echo.
    pause
    exit /b 1
)

exit /b 0
