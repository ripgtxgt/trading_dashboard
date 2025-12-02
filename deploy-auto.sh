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
echo "[2/5] Configuring environment variables..."
if [ -f .env.production.example ]; then
    # Backup existing .env if it exists
    if [ -f .env ]; then
        sudo cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo "Existing .env backed up"
    fi
    
    # Copy production template to .env
    sudo cp .env.production.example .env
    sudo chmod 600 .env
    sudo chown ubuntu:ubuntu .env
    echo "✓ Environment file updated from production template"
else
    echo "Warning: .env.production.example not found, skipping .env update"
fi

echo ""
echo "[3/5] Installing dependencies..."
pnpm install

echo ""
echo "[4/5] Building project..."
pnpm build

echo ""
echo "[5/5] Restarting PM2 services..."
# Restart trading-dashboard
pm2 restart trading-dashboard
echo "✓ trading-dashboard restarted"

# Restart trading-bot to apply new environment variables
if pm2 list | grep -q "trading-bot"; then
    pm2 restart trading-bot
    echo "✓ trading-bot restarted with new configuration"
fi

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
