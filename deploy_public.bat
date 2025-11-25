@echo off
REM One-Click Public Deployment Script for Trading Dashboard
REM Domain: cryptoalpha.vip
REM Phase 1: HTTP-only deployment (no SSL required)
REM Phase 2: Upgrade to HTTPS (run upgrade_to_https.bat after SSL setup)

echo ========================================
echo Trading Dashboard Public Deployment
echo ========================================
echo.
echo Domain: cryptoalpha.vip
echo Server IP: 13.113.194.218
echo.
echo DEPLOYMENT STRATEGY:
echo Phase 1: Deploy with HTTP only (this script)
echo Phase 2: Upgrade to HTTPS after SSL setup (upgrade_to_https.bat)
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

echo [INFO] Opening port 443 (HTTPS) for future use...
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
    echo Downloading Nginx...
    
    REM Try to download Nginx
    powershell -Command "& {Invoke-WebRequest -Uri 'http://nginx.org/download/nginx-1.24.0.zip' -OutFile '%TEMP%\nginx.zip'; Expand-Archive -Path '%TEMP%\nginx.zip' -DestinationPath 'C:\' -Force; Rename-Item 'C:\nginx-1.24.0' 'C:\nginx' -Force; Remove-Item '%TEMP%\nginx.zip'}" 2>nul
    
    if exist "C:\nginx\nginx.exe" (
        echo [SUCCESS] Nginx downloaded and installed
    ) else (
        echo [ERROR] Failed to download Nginx automatically
        echo.
        echo Please install Nginx manually:
        echo 1. Download from: http://nginx.org/en/download.html
        echo 2. Extract to C:\nginx
        echo 3. Run this script again
        echo.
        pause
        exit /b 1
    )
)
echo.

REM Step 3: Copy Nginx Configuration (HTTP-only)
echo ========================================
echo Step 3: Configuring Nginx (HTTP-only)
echo ========================================
echo.

if exist "nginx_http_only.conf" (
    echo [INFO] Copying HTTP-only Nginx configuration...
    copy /Y "nginx_http_only.conf" "C:\nginx\conf\nginx.conf" >nul
    echo [SUCCESS] Nginx configuration updated (HTTP-only mode)
    echo [INFO] HTTPS will be available after running upgrade_to_https.bat
) else (
    echo [ERROR] nginx_http_only.conf not found!
    pause
    exit /b 1
)

echo [INFO] Testing Nginx configuration...
cd C:\nginx
nginx -t 2>&1 | findstr /C:"syntax is ok" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] Nginx configuration is valid
) else (
    echo [ERROR] Nginx configuration test failed!
    echo.
    nginx -t
    echo.
    pause
    exit /b 1
)
echo.

REM Step 4: Check Dashboard Status
echo ========================================
echo Step 4: Checking Dashboard Status
echo ========================================
echo.

echo [INFO] Checking PM2 services...
call pm2 list 2>nul | findstr "trading-dashboard" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] PM2 is running
    call pm2 status
) else (
    echo [WARNING] PM2 services may not be running
    echo Please start Dashboard with: pm2 start ecosystem.config.cjs
)
echo.

echo [INFO] Testing Dashboard on localhost:3000...
curl -s http://localhost:3000 >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Dashboard is running on localhost:3000
) else (
    echo [WARNING] Dashboard may not be running
    echo.
    echo Starting Dashboard...
    call pm2 start ecosystem.config.cjs 2>nul
    timeout /t 3 >nul
    
    curl -s http://localhost:3000 >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Dashboard started successfully
    ) else (
        echo [ERROR] Failed to start Dashboard
        echo Please check: pm2 logs trading-dashboard
        pause
        exit /b 1
    )
)
echo.

REM Step 5: Start Nginx
echo ========================================
echo Step 5: Starting Nginx
echo ========================================
echo.

echo [INFO] Stopping existing Nginx processes...
taskkill /F /IM nginx.exe >nul 2>&1
timeout /t 1 >nul

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
    echo.
    echo Error log:
    type C:\nginx\logs\error.log
    echo.
    pause
    exit /b 1
)
echo.

REM Step 6: Verify Deployment
echo ========================================
echo Step 6: Deployment Verification
echo ========================================
echo.

echo [INFO] Checking port 80...
netstat -ano | findstr ":80" | findstr "LISTENING" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] Port 80 is listening
) else (
    echo [WARNING] Port 80 is not listening
)

echo [INFO] Testing HTTP access...
curl -s -o nul -w "HTTP Status: %%{http_code}" http://localhost >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] HTTP access is working
) else (
    echo [WARNING] HTTP access test failed
)
echo.

REM Final Summary
echo ========================================
echo Deployment Complete! (HTTP Mode)
echo ========================================
echo.
echo Your Trading Dashboard is now accessible at:
echo   - HTTP:  http://cryptoalpha.vip
echo   - Local: http://localhost
echo.
echo [IMPORTANT] DNS Configuration Required:
echo 1. Log in to your domain registrar (GoDaddy, Cloudflare, etc.)
echo 2. Add an A record:
echo    Type: A
echo    Name: @
echo    Value: 13.113.194.218
echo    TTL: 3600 (or Auto)
echo 3. Add another A record for www:
echo    Type: A
echo    Name: www
echo    Value: 13.113.194.218
echo    TTL: 3600 (or Auto)
echo 4. Wait 5-30 minutes for DNS propagation
echo 5. Test: nslookup cryptoalpha.vip
echo.
echo [NEXT STEPS] Upgrade to HTTPS:
echo 1. Run: setup_ssl.bat (to obtain SSL certificate)
echo 2. Run: upgrade_to_https.bat (to enable HTTPS)
echo.
echo Useful Commands:
echo   - Reload Nginx:  cd C:\nginx ^&^& nginx -s reload
echo   - Stop Nginx:    cd C:\nginx ^&^& nginx -s stop
echo   - View logs:     type C:\nginx\logs\error.log
echo   - PM2 status:    pm2 status
echo   - PM2 logs:      pm2 logs trading-dashboard
echo.
echo For detailed instructions, see: PUBLIC_DEPLOYMENT_GUIDE.md
echo.
pause
