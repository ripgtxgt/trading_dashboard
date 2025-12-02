#!/bin/bash
# Initialize MySQL database for trading-bot
# Run this script on the server to create database and user

set -e

echo "================================================"
echo "Trading Dashboard - Database Initialization"
echo "================================================"
echo ""

# Database configuration
DB_NAME="trading_dashboard"
DB_USER="trading"
DB_PASS="trading123"

echo "[1/3] Creating database..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};" 2>/dev/null || {
    echo "Error: Failed to create database. Make sure MySQL is running and you have sudo access."
    exit 1
}
echo "✓ Database created: ${DB_NAME}"

echo ""
echo "[2/3] Creating database user..."
sudo mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';" 2>/dev/null || true
sudo mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';" 2>/dev/null || true
sudo mysql -e "FLUSH PRIVILEGES;" 2>/dev/null || true
echo "✓ User created: ${DB_USER}"
echo "✓ Privileges granted"

echo ""
echo "[3/3] Verifying database connection..."
mysql -u${DB_USER} -p${DB_PASS} -h localhost ${DB_NAME} -e "SELECT 1 AS test;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Database connection successful"
else
    echo "✗ Database connection failed"
    exit 1
fi

echo ""
echo "================================================"
echo "Database initialization completed!"
echo "================================================"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 3306"
echo "  Database: ${DB_NAME}"
echo "  Username: ${DB_USER}"
echo "  Password: ${DB_PASS}"
echo ""
echo "DATABASE_URL=mysql://${DB_USER}:${DB_PASS}@localhost:3306/${DB_NAME}"
