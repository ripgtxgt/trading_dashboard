@echo off
echo ========================================
echo SQLite Fix Script
echo ========================================
echo.
echo This script will:
echo 1. Disable SQLite in the project
echo 2. Rebuild the project
echo 3. Restart trading-dashboard service
echo.
echo Press any key to continue...
pause >nul

powershell -ExecutionPolicy Bypass -File "%~dp0fix_sqlite.ps1"

echo.
echo ========================================
echo Script completed!
echo ========================================
echo.
pause
