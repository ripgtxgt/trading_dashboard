@echo off
REM One-Click Public Deployment Script for Trading Dashboard
REM Domain: cryptoalpha.vip
REM This script automates the deployment process

echo ========================================
echo Trading Dashboard Public Deployment
echo ========================================
echo.
echo Domain: cryptoalpha.vip
echo Server IP: 13.113.194.218
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [INFO] Running as Administrator
echo.

REM Step 1: Configure Firewall
echo ========================================
echo Step 1: Configuring Windows Firewall
echo ========================================
echo.
echo [INFO] Opening port 80 (HTTP)...
netsh advfirewall firewall add rule name="Allow HTTP" dir=in action=allow protocol=TCP localport=80 >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Port 80 opened
) else (
    echo [INFO] Port 80 rule already exists
)

echo [INFO] Opening port 443 (HTTPS)...
netsh advfirewall firewall add rule name="Allow HTTPS" dir=in action=allow protocol=TCP localport=443 >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Port 443 opened
) else (
    echo [INFO] Port 443 rule already exists
)
echo.

REM Step 2: Check Nginx Installation
echo ========================================
echo Step 2: Checking Nginx Installation
echo ========================================
echo.

if exist "C:\nginx\nginx.exe" (
    echo [SUCCESS] Nginx found at C:\nginx
) else (
    echo [WARNING] Nginx not found at C:\nginx
    echo.
    echo Please install Nginx first:
    echo 1. Download from: http://nginx.org/en/download.html
    echo 2. Extract to C:\nginx
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)
echo.

REM Step 3: Copy Nginx Configuration
echo ========================================
echo Step 3: Configuring Nginx
echo ========================================
echo.

if exist "nginx_windows.conf" (
    echo [INFO] Copying Nginx configuration...
    copy /Y "nginx_windows.conf" "C:\nginx\conf\nginx.conf" >nul
    echo [SUCCESS] Nginx configuration updated
) else (
    echo [ERROR] nginx_windows.conf not found!
    pause
    exit /b 1
)

echo [INFO] Testing Nginx configuration...
cd C:\nginx
nginx -t
if %errorLevel% neq 0 (
    echo [ERROR] Nginx configuration test failed!
    echo Please check the configuration file
    pause
    exit /b 1
)
echo [SUCCESS] Nginx configuration is valid
echo.

REM Step 4: SSL Certificate Setup
echo ========================================
echo Step 4: SSL Certificate Setup
echo ========================================
echo.
echo SSL certificate is required for HTTPS access.
echo.
echo Options:
echo 1. Run setup_ssl_windows.ps1 for automatic setup
echo 2. Place your own certificate files manually
echo 3. Generate self-signed certificate (testing only)
echo.

set /p ssl_choice="Do you want to setup SSL now? (yes/no): "
if /i "%ssl_choice%"=="yes" (
    echo.
    echo [INFO] Starting SSL setup...
    echo Please run: powershell -ExecutionPolicy Bypass -File setup_ssl_windows.ps1
    echo.
    echo Press Enter after SSL setup is complete...
    pause >nul
) else (
    echo.
    echo [WARNING] Skipping SSL setup
    echo You can run setup_ssl_windows.ps1 later
    echo.
)

REM Step 5: Check Dashboard Status
echo ========================================
echo Step 5: Checking Dashboard Status
echo ========================================
echo.

echo [INFO] Checking PM2 services...
call pm2 status
echo.

echo [INFO] Testing Dashboard on localhost:3000...
curl -s http://localhost:3000 >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Dashboard is running on localhost:3000
) else (
    echo [WARNING] Dashboard may not be running
    echo Please start Dashboard with: pm2 start ecosystem.config.cjs
    echo.
)
echo.

REM Step 6: Start Nginx
echo ========================================
echo Step 6: Starting Nginx
echo ========================================
echo.

echo [INFO] Stopping existing Nginx processes...
taskkill /F /IM nginx.exe >nul 2>&1

echo [INFO] Starting Nginx...
cd C:\nginx
start nginx

timeout /t 2 >nul

echo [INFO] Checking Nginx status...
tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I /N "nginx.exe">NUL
if %errorLevel% equ 0 (
    echo [SUCCESS] Nginx is running
) else (
    echo [ERROR] Failed to start Nginx
    echo Please check C:\nginx\logs\error.log for details
    pause
    exit /b 1
)
echo.

REM Step 7: Verify Deployment
echo ========================================
echo Step 7: Deployment Verification
echo ========================================
echo.

echo [INFO] Checking port 80...
netstat -ano | findstr ":80" | findstr "LISTENING" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] Port 80 is listening
) else (
    echo [WARNING] Port 80 is not listening
)

echo [INFO] Checking port 443...
netstat -ano | findstr ":443" | findstr "LISTENING" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] Port 443 is listening
) else (
    echo [WARNING] Port 443 is not listening (SSL may not be configured)
)
echo.

REM Final Summary
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your Trading Dashboard should now be accessible at:
echo   - HTTP:  http://cryptoalpha.vip
echo   - HTTPS: https://cryptoalpha.vip (if SSL is configured)
echo.
echo Important Notes:
echo 1. Make sure DNS A record points to: 13.113.194.218
echo 2. Wait 5-30 minutes for DNS propagation
echo 3. Configure SSL certificate for HTTPS access
echo 4. Check firewall rules on your cloud provider (AWS/Azure/etc.)
echo.
echo Useful Commands:
echo   - Reload Nginx:  cd C:\nginx ^&^& nginx -s reload
echo   - Stop Nginx:    cd C:\nginx ^&^& nginx -s stop
echo   - View logs:     type C:\nginx\logs\error.log
echo   - PM2 status:    pm2 status
echo.
echo For detailed instructions, see: PUBLIC_DEPLOYMENT_GUIDE.md
echo.
pause
