@echo off
REM ========================================
REM Start Webhook Deployment Server
REM ========================================
REM This server listens for GitHub push events
REM and automatically deploys the latest code
REM ========================================

echo.
echo ========================================
echo Starting Webhook Deployment Server
echo ========================================
echo.

cd /d C:\trading_dashboard_fixed

echo [INFO] Starting webhook server on port 9000...
echo [INFO] Press Ctrl+C to stop the server
echo.

node webhook-deploy-server.js

pause
