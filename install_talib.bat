@echo off
REM ===================================================================
REM TA-Lib Installation Wrapper for Windows
REM ===================================================================

echo ========================================
echo   TA-Lib Installation Tool
echo ========================================
echo.

echo Starting TA-Lib installation...
echo.

REM Run PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_talib_windows.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] TA-Lib installation failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo [OK] TA-Lib installation completed successfully
pause
