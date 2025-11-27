@echo off
chcp 65001 >nul
title Trading Dashboard - Simple Deployment

echo.
echo ========================================
echo   Trading Dashboard Deployment
echo   Simple Version
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires administrator privileges
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Run PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%~dp0simple-deploy.ps1"

pause
