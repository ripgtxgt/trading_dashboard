@echo off
REM ===================================================================
REM Database Initialization Wrapper for Windows
REM ===================================================================

echo ========================================
echo   Database Initialization Tool
echo ========================================
echo.

echo This tool will create:
echo   - Database: trading_dashboard
echo   - User: trading
echo   - Password: trading123 (default)
echo.

echo You will need to provide MySQL root password
echo.

pause

REM Run PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\init_database_windows.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Database initialization failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo [OK] Database initialization completed successfully
echo.
echo Next step: Update .env file with the connection string shown above
pause
