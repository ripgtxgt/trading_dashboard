#!/bin/bash
#
# Database Restore Script
# Restores MySQL database from backup file
# Usage: ./restore_database.sh <backup_file.sql.gz>
#

set -e

# Configuration
DB_NAME="trading_dashboard"
DB_USER="trading"
DB_PASS="trading123"

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lht /home/ubuntu/trading_dashboard/backups/trading_dashboard_*.sql.gz 2>/dev/null | head -10
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "================================================"
echo "Database Restore - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"
echo ""
echo "⚠️  WARNING: This will replace all data in the database!"
echo ""
echo "Backup file: ${BACKUP_FILE}"
echo "Database: ${DB_NAME}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo ""
echo "[1/3] Decompressing backup..."
TEMP_FILE="/tmp/trading_dashboard_restore_$$.sql"
gunzip -c "${BACKUP_FILE}" > "${TEMP_FILE}"
if [ $? -eq 0 ]; then
    RESTORE_SIZE=$(du -h "${TEMP_FILE}" | cut -f1)
    echo "✓ Backup decompressed: ${TEMP_FILE}"
    echo "  Size: ${RESTORE_SIZE}"
else
    echo "✗ Decompression failed"
    exit 1
fi

echo ""
echo "[2/3] Restoring database..."
mysql -u${DB_USER} -p${DB_PASS} ${DB_NAME} < "${TEMP_FILE}" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database restored successfully"
else
    echo "✗ Database restore failed"
    rm -f "${TEMP_FILE}"
    exit 1
fi

echo ""
echo "[3/3] Cleaning up..."
rm -f "${TEMP_FILE}"
echo "✓ Temporary files removed"

echo ""
echo "================================================"
echo "Restore completed successfully!"
echo "================================================"
echo ""
echo "Database: ${DB_NAME}"
echo "Restored from: ${BACKUP_FILE}"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

exit 0
