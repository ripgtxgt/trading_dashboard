#!/bin/bash
#
# Database Backup Script
# Backs up MySQL database to local directory and optionally to cloud storage
# Run daily via cron: 0 2 * * * /home/ubuntu/trading_dashboard/scripts/backup_database.sh
#

set -e

# Configuration
DB_NAME="trading_dashboard"
DB_USER="trading"
DB_PASS="trading123"
BACKUP_DIR="/home/ubuntu/trading_dashboard/backups"
RETENTION_DAYS=30  # Keep backups for 30 days

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/trading_dashboard_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

echo "================================================"
echo "Database Backup - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"
echo ""

# Perform database backup
echo "[1/4] Backing up database..."
mysqldump -u${DB_USER} -p${DB_PASS} ${DB_NAME} > "${BACKUP_FILE}" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database backup created: ${BACKUP_FILE}"
    
    # Get backup file size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "  Size: ${BACKUP_SIZE}"
else
    echo "✗ Database backup failed"
    exit 1
fi

# Compress backup
echo ""
echo "[2/4] Compressing backup..."
gzip "${BACKUP_FILE}"
if [ $? -eq 0 ]; then
    COMPRESSED_SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
    echo "✓ Backup compressed: ${COMPRESSED_FILE}"
    echo "  Size: ${COMPRESSED_SIZE}"
else
    echo "✗ Compression failed"
    exit 1
fi

# Clean up old backups
echo ""
echo "[3/4] Cleaning up old backups..."
DELETED_COUNT=0
find "${BACKUP_DIR}" -name "trading_dashboard_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete 2>/dev/null && DELETED_COUNT=$?
echo "✓ Deleted backups older than ${RETENTION_DAYS} days"

# List current backups
echo ""
echo "[4/4] Current backups:"
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/trading_dashboard_*.sql.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" 2>/dev/null | cut -f1)
echo "  Count: ${BACKUP_COUNT} files"
echo "  Total size: ${TOTAL_SIZE}"

# Show latest 5 backups
echo ""
echo "Latest backups:"
ls -lht "${BACKUP_DIR}"/trading_dashboard_*.sql.gz 2>/dev/null | head -5 | awk '{printf "  %s %s  %s\n", $6, $7, $9}'

echo ""
echo "================================================"
echo "Backup completed successfully!"
echo "================================================"
echo ""
echo "Backup location: ${COMPRESSED_FILE}"
echo ""

# Optional: Send notification via Telegram
# Uncomment the following lines to enable Telegram notifications
# if [ -f .env ]; then
#     source .env
#     if [ ! -z "$TELEGRAM_BOT_TOKEN" ] && [ ! -z "$TELEGRAM_CHAT_ID" ]; then
#         MESSAGE="✅ Database Backup Completed\n\nServer: cryptoalpha.vip\nDatabase: ${DB_NAME}\nSize: ${COMPRESSED_SIZE}\nTime: $(date '+%Y-%m-%d %H:%M:%S')"
#         curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
#             -d "chat_id=${TELEGRAM_CHAT_ID}" \
#             -d "text=${MESSAGE}" \
#             -d "parse_mode=Markdown" > /dev/null
#     fi
# fi

exit 0
