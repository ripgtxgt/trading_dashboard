@echo off
REM Upgrade to HTTPS Script
REM Run this after SSL certificate is configured
REM Switches from HTTP-only to HTTPS configuration

echo ========================================
echo Upgrade to HTTPS
echo ========================================
echo.
echo This script will upgrade your deployment to HTTPS.
echo.
echo PREREQUISITES:
echo 1. SSL certificate files must be in place
echo 2. HTTP deployment must be working
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

REM Check SSL certificate files
echo ========================================
echo Step 1: Checking SSL Certificate
echo ========================================
echo.

set SSL_DIR=C:\nginx\ssl\cryptoalpha.vip
set CERT_FILE=%SSL_DIR%\fullchain.pem
set KEY_FILE=%SSL_DIR%\privkey.pem

echo [INFO] Checking for SSL certificate files...
if exist "%CERT_FILE%" (
    echo [SUCCESS] Certificate found: %CERT_FILE%
) else (
    echo [ERROR] Certificate not found: %CERT_FILE%
    echo.
    echo Please run setup_ssl.bat first to obtain SSL certificate
    pause
    exit /b 1
)

if exist "%KEY_FILE%" (
    echo [SUCCESS] Private key found: %KEY_FILE%
) else (
    echo [ERROR] Private key not found: %KEY_FILE%
    echo.
    echo Please run setup_ssl.bat first to obtain SSL certificate
    pause
    exit /b 1
)
echo.

REM Backup current configuration
echo ========================================
echo Step 2: Backing Up Configuration
echo ========================================
echo.

echo [INFO] Creating backup of current configuration...
copy /Y "C:\nginx\conf\nginx.conf" "C:\nginx\conf\nginx.conf.backup" >nul
echo [SUCCESS] Backup created: C:\nginx\conf\nginx.conf.backup
echo.

REM Copy HTTPS configuration
echo ========================================
echo Step 3: Updating Nginx Configuration
echo ========================================
echo.

if exist "nginx_windows.conf" (
    echo [INFO] Copying HTTPS configuration...
    copy /Y "nginx_windows.conf" "C:\nginx\conf\nginx.conf" >nul
    echo [SUCCESS] Nginx configuration updated (HTTPS enabled)
) else (
    echo [ERROR] nginx_windows.conf not found!
    echo.
    echo Restoring backup...
    copy /Y "C:\nginx\conf\nginx.conf.backup" "C:\nginx\conf\nginx.conf" >nul
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
    echo Restoring backup...
    copy /Y "C:\nginx\conf\nginx.conf.backup" "C:\nginx\conf\nginx.conf" >nul
    pause
    exit /b 1
)
echo.

REM Reload Nginx
echo ========================================
echo Step 4: Reloading Nginx
echo ========================================
echo.

echo [INFO] Reloading Nginx with new configuration...
cd C:\nginx
nginx -s reload 2>nul

if %errorLevel% equ 0 (
    echo [SUCCESS] Nginx reloaded successfully
) else (
    echo [WARNING] Reload command failed, restarting Nginx...
    
    taskkill /F /IM nginx.exe >nul 2>&1
    timeout /t 1 >nul
    start nginx
    timeout /t 2 >nul
    
    tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I /N "nginx.exe">NUL
    if %errorLevel% equ 0 (
        echo [SUCCESS] Nginx restarted successfully
    ) else (
        echo [ERROR] Failed to restart Nginx
        echo.
        echo Restoring backup...
        copy /Y "C:\nginx\conf\nginx.conf.backup" "C:\nginx\conf\nginx.conf" >nul
        start nginx
        pause
        exit /b 1
    )
)
echo.

REM Verify HTTPS
echo ========================================
echo Step 5: Verifying HTTPS
echo ========================================
echo.

echo [INFO] Checking port 443...
netstat -ano | findstr ":443" | findstr "LISTENING" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] Port 443 is listening
) else (
    echo [WARNING] Port 443 is not listening
)

echo [INFO] Testing HTTPS access...
curl -k -s -o nul -w "HTTPS Status: %%{http_code}" https://localhost >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] HTTPS access is working
) else (
    echo [WARNING] HTTPS access test failed (this is normal if DNS is not configured yet)
)
echo.

REM Final Summary
echo ========================================
echo HTTPS Upgrade Complete!
echo ========================================
echo.
echo Your Trading Dashboard is now accessible at:
echo   - HTTP:  http://cryptoalpha.vip (redirects to HTTPS)
echo   - HTTPS: https://cryptoalpha.vip (secure)
echo.
echo [IMPORTANT] Verify HTTPS:
echo 1. Open browser and visit: https://cryptoalpha.vip
echo 2. Check for green padlock icon (secure connection)
echo 3. Verify certificate is valid
echo.
echo [TROUBLESHOOTING]
echo If HTTPS doesn't work:
echo 1. Check DNS is configured correctly: nslookup cryptoalpha.vip
echo 2. Check certificate files exist in: %SSL_DIR%
echo 3. Check Nginx error log: type C:\nginx\logs\error.log
echo 4. Restore HTTP-only: copy /Y C:\nginx\conf\nginx.conf.backup C:\nginx\conf\nginx.conf
echo.
echo Configuration backup saved at:
echo   C:\nginx\conf\nginx.conf.backup
echo.
echo Useful Commands:
echo   - Reload Nginx:  cd C:\nginx ^&^& nginx -s reload
echo   - Stop Nginx:    cd C:\nginx ^&^& nginx -s stop
echo   - View logs:     type C:\nginx\logs\error.log
echo   - Restore HTTP:  copy /Y C:\nginx\conf\nginx.conf.backup C:\nginx\conf\nginx.conf
echo.
pause
