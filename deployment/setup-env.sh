#!/bin/bash
# Setup environment variables for trading-bot
# This script will create/update the .env file on the server

set -e

echo "================================================"
echo "Trading Bot Environment Configuration"
echo "================================================"
echo ""

# Database configuration
DB_NAME="trading_dashboard"
DB_USER="trading"
DB_PASS="trading123"
DB_HOST="localhost"
DB_PORT="3306"

echo "[1/5] Creating database and user..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};" 2>/dev/null || true
sudo mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';" 2>/dev/null || true
sudo mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';" 2>/dev/null || true
sudo mysql -e "FLUSH PRIVILEGES;" 2>/dev/null || true
echo "✓ Database created: ${DB_NAME}"
echo "✓ User created: ${DB_USER}"

# Create .env file
ENV_FILE="/home/ubuntu/trading_dashboard/.env"

echo ""
echo "[2/5] Creating .env file..."

cat > ${ENV_FILE} << 'EOF'
# KuCoin API Configuration
KUCOIN_API_KEY=67466c3e8df5f50001d0a9f8
KUCOIN_API_SECRET=c5e3e6df-e2f0-4b6f-b9f0-d4e0c3b6e8a9
KUCOIN_API_PASSPHRASE=Zdm351026
KUCOIN_SANDBOX=false

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U
TELEGRAM_CHAT_ID=5374455360

# Database Configuration
DATABASE_URL=mysql://trading:trading123@localhost:3306/trading_dashboard

# Trading Configuration
INITIAL_CAPITAL=auto
EOF

echo "✓ .env file created at ${ENV_FILE}"

echo ""
echo "[3/5] Setting file permissions..."
chmod 600 ${ENV_FILE}
echo "✓ File permissions set to 600 (owner read/write only)"

echo ""
echo "[4/5] Verifying database connection..."
mysql -u${DB_USER} -p${DB_PASS} -h${DB_HOST} -P${DB_PORT} ${DB_NAME} -e "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Database connection successful"
else
    echo "✗ Database connection failed"
    exit 1
fi

echo ""
echo "[5/5] Configuration summary:"
echo "  Database: ${DB_NAME}"
echo "  Database User: ${DB_USER}"
echo "  KuCoin Sandbox: false (LIVE TRADING)"
echo "  Initial Capital: auto-detect from account"
echo ""
echo "================================================"
echo "Configuration completed successfully!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Restart trading-bot: pm2 restart trading-bot"
echo "  2. Check logs: pm2 logs trading-bot"
echo "  3. Monitor status: pm2 list"
