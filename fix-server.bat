@echo off
REM ========================================
REM Server Fix Script
REM ========================================
REM This script fixes common deployment issues:
REM 1. Git repository corruption
REM 2. Missing patches files
REM 3. Missing dependencies
REM ========================================

echo.
echo ========================================
echo Server Fix Script
echo ========================================
echo.

cd /d C:\trading_dashboard_fixed

echo [INFO] Step 1: Resetting git repository...
echo [INFO] This will discard all local changes and restore from GitHub
echo.

REM Reset git index
git reset HEAD .
git checkout -- .

REM If still corrupted, force reset
git fetch --all
git reset --hard origin/main
git clean -fd

echo [SUCCESS] Git repository reset complete
echo.

echo [INFO] Step 2: Copying .env file from C:\.env...
if exist "C:\.env" (
    copy /Y "C:\.env" ".env"
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] .env file copied successfully
    ) else (
        echo [ERROR] Failed to copy .env file
    )
) else (
    echo [WARNING] C:\.env file not found
    echo [INFO] Please create C:\.env file with your configuration
    if not exist ".env" (
        echo [WARNING] No .env file in project directory either
        echo [INFO] Services requiring environment variables will fail to start
    )
)
echo.

echo [INFO] Step 3: Verifying critical files...
if not exist "package.json" (
    echo [ERROR] Critical files missing! Repository is corrupted.
    echo [INFO] Performing full repository restore...
    
    cd ..
    if exist "trading_dashboard_fixed_backup" rmdir /s /q trading_dashboard_fixed_backup
    move trading_dashboard_fixed trading_dashboard_fixed_backup
    
    echo [INFO] Cloning fresh repository from GitHub...
    git clone https://github.com/ripgtxgt/trading_dashboard.git trading_dashboard_fixed
    cd trading_dashboard_fixed
    
    echo [SUCCESS] Repository cloned successfully
) else (
    echo [SUCCESS] Critical files verified
)

echo.
echo [INFO] Step 4: Verifying patches directory...
if not exist "patches" mkdir patches

if not exist "patches\wouter@3.7.1.patch" (
    echo [WARNING] wouter patch file missing!
    echo [INFO] Downloading patch file from GitHub...
    curl -L "https://raw.githubusercontent.com/ripgtxgt/trading_dashboard/main/patches/wouter@3.7.1.patch" -o "patches\wouter@3.7.1.patch"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to download patch file
        echo [INFO] Continuing without patch...
    ) else (
        echo [SUCCESS] Patch file downloaded
    )
) else (
    echo [SUCCESS] Patch file exists
)

echo.
echo [INFO] Step 5: Cleaning and reinstalling dependencies...
if exist "node_modules" (
    echo [INFO] Removing old node_modules...
    rmdir /s /q node_modules
)

if exist "pnpm-lock.yaml" del pnpm-lock.yaml

echo [INFO] Installing dependencies with pnpm...
echo [INFO] This may take a few minutes, please wait...
echo.
call pnpm install --no-frozen-lockfile
set INSTALL_EXIT_CODE=%ERRORLEVEL%
echo.
if %INSTALL_EXIT_CODE% NEQ 0 (
    echo [ERROR] pnpm install failed
    echo [INFO] Trying with --force flag...
    echo.
    call pnpm install --force --no-frozen-lockfile
    set INSTALL_EXIT_CODE=%ERRORLEVEL%
    echo.
    if %INSTALL_EXIT_CODE% NEQ 0 (
        echo [ERROR] Installation failed completely
        echo [INFO] Please check your internet connection and pnpm installation
        pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] Dependencies installed
echo.

echo [INFO] Step 6: Building project...
echo [INFO] This may take a few minutes, please wait...
echo.
call pnpm run build
set BUILD_EXIT_CODE=%ERRORLEVEL%
echo.
if %BUILD_EXIT_CODE% NEQ 0 (
    echo [ERROR] Build failed
    echo [INFO] Check the error messages above
    pause
    exit /b 1
)

echo [SUCCESS] Build completed
echo.

echo [INFO] Step 7: Copying build files to server directory...
if not exist "server\_core\public" mkdir server\_core\public
if exist "dist\public" (
    echo [INFO] Copying dist\public to server\_core\public...
    xcopy /E /I /Y "dist\public\*" "server\_core\public\"
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Build files copied to server directory
    ) else (
        echo [ERROR] Failed to copy build files
    )
) else (
    echo [WARNING] dist\public not found
)
echo.

echo [INFO] Step 8: Setting up logs directory...
if not exist "logs" mkdir logs

echo.
echo [INFO] Step 9: Restarting PM2 services...
echo [INFO] Stopping existing services...
call pm2 delete all 2>nul
echo.
echo [INFO] Starting services from ecosystem.config.cjs...
call pm2 start ecosystem.config.cjs
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start PM2 services
    echo [INFO] Check ecosystem.config.cjs for errors
    pause
    exit /b 1
)
echo.
echo [INFO] Saving PM2 process list...
call pm2 save
echo.
echo [SUCCESS] PM2 services started
echo.

echo [INFO] Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [SUCCESS] =========================================
echo [SUCCESS] Server fixed successfully!
echo [SUCCESS] =========================================
echo.
echo [INFO] Service status:
pm2 list
echo.
echo [INFO] Next steps:
echo 1. Check logs: pm2 logs
echo 2. Access dashboard: http://localhost:3000
echo 3. If issues persist, check individual service logs
echo.

pause
