#!/bin/bash
set -e

# Trading Simulator Server Setup Script
# This script sets up a fresh Ubuntu server for the trading simulator

APP_DIR="/opt/trading-sim"
APP_USER="www-data"
DB_NAME="trading_sim"
DB_USER="trading_user"

echo "Setting up Trading Simulator server..."

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Update system
log "Updating system packages"
apt update && apt upgrade -y

# Install required packages
log "Installing required packages"
apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    certbot python3-certbot-nginx \
    build-essential \
    git \
    curl \
    htop \
    logrotate

# Create application directory
log "Creating application directory"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/instance"
mkdir -p /opt/backups/trading-sim

# Set up PostgreSQL
log "Setting up PostgreSQL"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD 'secure_password_here';" || true
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" || true

# Configure Redis
log "Configuring Redis"
systemctl enable redis-server
systemctl start redis-server

# Set up application user permissions
log "Setting up application permissions"
chown -R $APP_USER:$APP_USER "$APP_DIR"
chmod 755 "$APP_DIR"
chmod -R 755 "$APP_DIR/logs"
chmod -R 755 "$APP_DIR/instance"

# Create Python virtual environment
log "Creating Python virtual environment"
sudo -u $APP_USER python3 -m venv "$APP_DIR/venv"

# Create environment file template
log "Creating environment file template"
cat > "$APP_DIR/.env.template" << EOF
FLASK_SECRET_KEY=generate-a-secure-secret-key-here
APP_BASE_URL=https://your-domain.com
FLASK_ENV=production
MARKET_TIMEZONE=America/New_York

DATABASE_URL=postgresql://$DB_USER:secure_password_here@localhost/$DB_NAME

REDIS_URL=redis://localhost:6379/0
SESSION_TYPE=redis
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=True

TICK_INTERVAL_SECS=2
DEFAULT_DRIFT=0.0001
DEFAULT_VOLATILITY=0.02
MAX_TICK_PCT=0.05

ADMIN_EMAIL=admin@your-domain.com
ADMIN_PASSWORD=change-this-password

# Optional
SENTRY_DSN=
EOF

chown $APP_USER:$APP_USER "$APP_DIR/.env.template"

# Install systemd services
log "Installing systemd services"
cp systemd/*.service /etc/systemd/system/
cp systemd/*.timer /etc/systemd/system/
systemctl daemon-reload

# Configure NGINX
log "Configuring NGINX"
cp nginx/trading-sim /etc/nginx/sites-available/
# Note: Don't enable the site yet - need to configure domain and SSL first

# Add rate limiting to nginx.conf
if ! grep -q "limit_req_zone" /etc/nginx/nginx.conf; then
    sed -i '/http {/a \    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;' /etc/nginx/nginx.conf
fi

# Set up log rotation
log "Setting up log rotation"
cat > /etc/logrotate.d/trading-sim << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su $APP_USER $APP_USER
}

/var/log/nginx/trading-sim*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        systemctl reload nginx
    endscript
}
EOF

# Create firewall rules
log "Configuring firewall"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create deployment user (optional)
log "Creating deployment user"
useradd -m -s /bin/bash deploy || true
usermod -aG sudo deploy || true
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chown deploy:deploy /home/deploy/.ssh

log "Server setup completed!"
log ""
log "Next steps:"
log "1. Copy your application code to $APP_DIR"
log "2. Copy .env.template to .env and configure with real values"
log "3. Update NGINX configuration with your domain name"
log "4. Install SSL certificate: certbot --nginx -d your-domain.com"
log "5. Run database migrations: sudo -u $APP_USER $APP_DIR/venv/bin/flask db upgrade"
log "6. Start services: systemctl enable --now trading-web trading-worker"
log ""
log "Configuration files:"
log "- Application: $APP_DIR"
log "- Environment: $APP_DIR/.env (copy from .env.template)"
log "- NGINX: /etc/nginx/sites-available/trading-sim"
log "- Systemd: /etc/systemd/system/trading-*.service"
log ""
log "Useful commands:"
log "- Check logs: journalctl -u trading-web -u trading-worker -f"
log "- Restart services: systemctl restart trading-web trading-worker"
log "- Check status: systemctl status trading-web trading-worker"