#!/bin/bash
set -e

# ZEBRAT TRADING Backup Script

APP_DIR="/opt/trading-sim"
BACKUP_DIR="/opt/backups/trading-sim"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "Starting backup at $(date)"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application files
log "Backing up application files"
tar -czf "$BACKUP_DIR/app-$TIMESTAMP.tar.gz" \
    -C "$APP_DIR" \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .

# Backup database
log "Backing up database"
sudo -u postgres pg_dump trading_sim | gzip > "$BACKUP_DIR/db-$TIMESTAMP.sql.gz"

# Backup audit logs and cash ledger separately
log "Backing up audit and cash ledger data"
sudo -u postgres pg_dump -t audit_log -t cash_ledger trading_sim | gzip > "$BACKUP_DIR/audit-cash-$TIMESTAMP.sql.gz"

# Backup system configuration
log "Backing up system configuration"
tar -czf "$BACKUP_DIR/config-$TIMESTAMP.tar.gz" \
    /etc/nginx/sites-available/trading-sim \
    /etc/systemd/system/trading-*.service \
    /etc/systemd/system/trading-*.timer \
    2>/dev/null || true

# Calculate sizes
APP_SIZE=$(du -h "$BACKUP_DIR/app-$TIMESTAMP.tar.gz" | cut -f1)
DB_SIZE=$(du -h "$BACKUP_DIR/db-$TIMESTAMP.sql.gz" | cut -f1)

log "Backup completed:"
log "- Application: $APP_SIZE"
log "- Database: $DB_SIZE"

# Clean up old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)"
find "$BACKUP_DIR" -name "*.tar.gz" -o -name "*.sql.gz" | \
    xargs -r ls -t | \
    tail -n +$((RETENTION_DAYS * 3 + 1)) | \
    xargs -r rm -f

# Show backup status
log "Current backups:"
ls -lh "$BACKUP_DIR"

echo "Backup completed at $(date)"