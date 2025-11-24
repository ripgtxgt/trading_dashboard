@echo off
REM ===================================================================
REM Install Python Dependencies
REM This script installs all required Python packages
REM ===================================================================

echo.
echo ========================================
echo Installing Python Dependencies
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python version:
python --version

echo.
echo [INFO] Installing dependencies from requirements.txt...
echo.

REM Install dependencies
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete
echo ========================================
echo.
echo All Python dependencies have been installed successfully
echo.

pause
