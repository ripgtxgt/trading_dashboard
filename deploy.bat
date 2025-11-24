@echo off
title Automated Deployment Tool

echo ========================================
echo   Trading Dashboard - Auto Deployment
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Recommend running as Administrator
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    set /p continue="Continue anyway? (Enter Y to continue): "
    if /i not "%continue%"=="Y" (
        echo Deployment cancelled
        pause
        exit /b 0
    )
)

echo.
echo Starting automated deployment...
echo.

REM Switch to script directory
cd /d "%~dp0"

REM Run PowerShell deployment script
powershell -ExecutionPolicy Bypass -File "scripts\deploy_windows.ps1"

REM Check if PowerShell execution failed
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Deployment script failed
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.

pause
exit /b 0
