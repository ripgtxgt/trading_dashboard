@echo off
REM ========================================
REM Force Sync Script - 强制同步GitHub最新代码
REM ========================================
REM This script will:
REM 1. Discard ALL local changes
REM 2. Force pull from GitHub
REM 3. Rebuild everything from scratch
REM 4. Restart all services
REM ========================================

echo.
echo ========================================
echo Force Sync from GitHub
echo ========================================
echo.
echo [WARNING] This will discard ALL local changes!
echo [WARNING] Press Ctrl+C to cancel, or
pause

cd /d C:\trading_dashboard_fixed

echo.
echo [INFO] Step 1: Cleaning local repository...
echo [INFO] Discarding all local changes...
echo.

REM Discard all local changes
git reset --hard HEAD
git clean -fd

echo [SUCCESS] Local changes discarded
echo.

echo [INFO] Step 2: Fetching latest code from GitHub...
echo.

REM Fetch all branches
call git fetch --all --prune
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to fetch from GitHub
    echo [INFO] Check your internet connection
    pause
    exit /b 1
)

echo [SUCCESS] Fetched latest code
echo.

echo [INFO] Step 3: Force reset to GitHub main branch...
echo.

REM Force reset to origin/main
call git reset --hard origin/main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to reset to origin/main
    pause
    exit /b 1
)

echo [SUCCESS] Reset to latest GitHub code
echo.

echo [INFO] Step 4: Verifying current commit...
echo.
git log -1 --oneline
echo.

echo [INFO] Step 5: Copying .env file...
if exist "C:\.env" (
    copy /Y "C:\.env" ".env"
    echo [SUCCESS] .env file copied
) else (
    echo [WARNING] C:\.env not found
)
echo.

echo [INFO] Step 6: Cleaning build artifacts...
if exist "node_modules" rmdir /s /q node_modules
if exist "dist" rmdir /s /q dist
if exist "pnpm-lock.yaml" del pnpm-lock.yaml
echo [SUCCESS] Build artifacts cleaned
echo.

echo [INFO] Step 7: Installing dependencies...
echo [INFO] This may take a few minutes...
echo.
call pnpm install --no-frozen-lockfile
set INSTALL_EXIT_CODE=%ERRORLEVEL%
echo.
if %INSTALL_EXIT_CODE% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
echo.

echo [INFO] Step 8: Building project...
echo [INFO] This may take a few minutes...
echo.
call pnpm run build
set BUILD_EXIT_CODE=%ERRORLEVEL%
echo.
if %BUILD_EXIT_CODE% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [SUCCESS] Build completed
echo.

echo [INFO] Step 9: Copying build files to server directory...
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

echo [INFO] Step 10: Restarting all services...
echo.
call pm2 delete all 2>nul
call pm2 start ecosystem.config.cjs
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
call pm2 save
echo.
echo [SUCCESS] Services restarted
echo.

echo [INFO] Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [SUCCESS] =========================================
echo [SUCCESS] Force sync completed successfully!
echo [SUCCESS] =========================================
echo.
echo [INFO] Current version:
git log -1 --pretty=format:"Commit: %%h - %%s" && echo.
echo.
echo [INFO] Service status:
pm2 list
echo.
echo [INFO] Next steps:
echo 1. Access dashboard: http://localhost:3000
echo 2. Check logs: pm2 logs
echo 3. Verify all features are working
echo.

pause
