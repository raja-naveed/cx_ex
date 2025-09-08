#!/bin/bash
set -e

# ZEBRAT TRADING Restore Script

APP_DIR="/opt/trading-sim"
BACKUP_DIR="/opt/backups/trading-sim"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Function to show usage
usage() {
    echo "Usage: $0 <backup_timestamp>"
    echo "Example: $0 20240101_120000"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR" | grep -E "(app-|db-)" | sed 's/^/  /' | sort
    exit 1
}

# Check arguments
if [ $# -ne 1 ]; then
    usage
fi

TIMESTAMP=$1
APP_BACKUP="$BACKUP_DIR/app-$TIMESTAMP.tar.gz"
DB_BACKUP="$BACKUP_DIR/db-$TIMESTAMP.sql.gz"

# Check if backup files exist
if [ ! -f "$APP_BACKUP" ]; then
    log "ERROR: Application backup not found: $APP_BACKUP"
    usage
fi

if [ ! -f "$DB_BACKUP" ]; then
    log "ERROR: Database backup not found: $DB_BACKUP"
    usage
fi

# Confirmation
echo "This will restore ZEBRAT TRADING from backup timestamp: $TIMESTAMP"
echo "Current application will be stopped and replaced."
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Stop services
log "Stopping services"
systemctl stop trading-worker || true
systemctl stop trading-web || true

# Backup current state (just in case)
RESTORE_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
log "Creating safety backup before restore"
if [ -d "$APP_DIR" ]; then
    tar -czf "$BACKUP_DIR/pre-restore-$RESTORE_TIMESTAMP.tar.gz" -C "$APP_DIR" .
fi
sudo -u postgres pg_dump trading_sim | gzip > "$BACKUP_DIR/pre-restore-db-$RESTORE_TIMESTAMP.sql.gz" 2>/dev/null || true

# Restore application files
log "Restoring application files"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"
tar -xzf "$APP_BACKUP" -C "$APP_DIR"
chown -R www-data:www-data "$APP_DIR"

# Restore database
log "Restoring database"
sudo -u postgres dropdb trading_sim || true
sudo -u postgres createdb trading_sim -O trading_user
zcat "$DB_BACKUP" | sudo -u postgres psql trading_sim

# Recreate virtual environment
log "Recreating virtual environment"
sudo -u www-data python3 -m venv "$APP_DIR/venv"
sudo -u www-data "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# Start services
log "Starting services"
systemctl start trading-web
systemctl start trading-worker

# Wait for services to start
sleep 10

# Check service status
if ! systemctl is-active --quiet trading-web; then
    log "ERROR: Web service failed to start"
    exit 1
fi

if ! systemctl is-active --quiet trading-worker; then
    log "ERROR: Worker service failed to start"
    exit 1
fi

# Test application health
log "Testing application health"
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "WARNING: Health check failed, but services are running"
fi

log "Restore completed successfully at $(date)"
log "Application is running at http://localhost:8000"
log ""
log "Safety backups created:"
log "- Application: pre-restore-$RESTORE_TIMESTAMP.tar.gz"
log "- Database: pre-restore-db-$RESTORE_TIMESTAMP.sql.gz"