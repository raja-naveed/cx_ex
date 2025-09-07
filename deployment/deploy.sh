#!/bin/bash
set -e

# Trading Simulator Deployment Script
# This script deploys the application to production

APP_DIR="/opt/trading-sim"
APP_USER="www-data"
BACKUP_DIR="/opt/backups/trading-sim"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting deployment at $(date)"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to rollback on error
rollback() {
    log "ERROR: Deployment failed. Rolling back..."
    if [ -d "${APP_DIR}.backup" ]; then
        sudo rm -rf "$APP_DIR"
        sudo mv "${APP_DIR}.backup" "$APP_DIR"
        sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
        sudo systemctl start trading-web
        sudo systemctl start trading-worker
    fi
    exit 1
}

# Set up error handling
trap rollback ERR

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Backup current deployment
log "Creating backup of current deployment"
if [ -d "$APP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    sudo cp -r "$APP_DIR" "${APP_DIR}.backup"
    sudo tar -czf "$BACKUP_DIR/trading-sim-$TIMESTAMP.tar.gz" -C "$APP_DIR" .
fi

# Stop services
log "Stopping services"
sudo systemctl stop trading-worker || true
sudo systemctl stop trading-web || true

# Update application code
log "Updating application code"
# Assuming code is already uploaded to /tmp/trading-sim
if [ -d "/tmp/trading-sim" ]; then
    sudo rsync -av --exclude='.env' --exclude='instance/' --exclude='logs/' /tmp/trading-sim/ $APP_DIR/
else
    log "No new code found in /tmp/trading-sim"
fi

# Set correct permissions
log "Setting permissions"
sudo chown -R $APP_USER:$APP_USER "$APP_DIR"
sudo chmod +x "$APP_DIR/simple_price_worker.py"
sudo chmod +x "$APP_DIR/market_scheduler.py"

# Install/update Python dependencies
log "Installing Python dependencies"
cd "$APP_DIR"
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Run database migrations
log "Running database migrations"
sudo -u $APP_USER $APP_DIR/venv/bin/flask db upgrade

# Collect static files (if needed)
log "Processing static files"
# Flask serves static files directly, no collection needed

# Start services
log "Starting services"
sudo systemctl start trading-web
sudo systemctl start trading-worker
sudo systemctl enable trading-web
sudo systemctl enable trading-worker

# Wait for services to start
log "Waiting for services to start"
sleep 10

# Check service status
if ! sudo systemctl is-active --quiet trading-web; then
    log "Web service failed to start"
    rollback
fi

if ! sudo systemctl is-active --quiet trading-worker; then
    log "Worker service failed to start"
    rollback
fi

# Test application health
log "Testing application health"
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "Health check failed"
    rollback
fi

# Clean up old backups (keep last 5)
log "Cleaning up old backups"
ls -t $BACKUP_DIR/trading-sim-*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f

# Remove temporary backup
sudo rm -rf "${APP_DIR}.backup"

log "Deployment completed successfully at $(date)"
log "Application is running at http://localhost:8000"