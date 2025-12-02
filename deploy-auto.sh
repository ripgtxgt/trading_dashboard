#!/bin/bash
# Auto-deployment script for Linux (Ubuntu)
# This script is called by webhook-deploy-server.cjs

set -e  # Exit on error

echo "=========================================="
echo "Starting Auto-Deployment"
echo "Time: $(date)"
echo "=========================================="

# Project directory
PROJECT_DIR="/home/ubuntu/trading_dashboard"
cd "$PROJECT_DIR"

echo ""
echo "[1/5] Pulling latest code from GitHub..."
git pull origin main

echo ""
echo "[2/5] Installing dependencies..."
pnpm install

echo ""
echo "[3/5] Building project..."
pnpm build

echo ""
echo "[4/5] Restarting PM2 services..."
# Only restart trading-dashboard, not webhook-deploy-server to avoid interrupting deployment
pm2 restart trading-dashboard

echo ""
echo "[5/5] Checking service status..."
pm2 list

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "Time: $(date)"
echo "=========================================="

# Check if Nginx is running
if systemctl is-active --quiet nginx; then
    echo "Nginx is running"
else
    echo "Nginx is not running, starting..."
    sudo systemctl start nginx
fi

exit 0
