# ZEBRAT TRADING

A comprehensive Flask-based trading simulator with real-time price simulation, portfolio management, and administrative controls.

## Features

### Core Trading System
- **Real-time Price Simulation**: Random walk algorithm with configurable drift and volatility
- **Market Orders**: Buy/sell orders executed at current market prices
- **Portfolio Management**: Track positions, P&L, and cash balances
- **Market Hours**: Configurable trading hours with holiday calendar
- **Order Queue**: Orders placed during closed market hours are queued for execution

### User Management
- **Customer Accounts**: Registration, login, and session management
- **Admin Interface**: Stock management, market controls, and system monitoring
- **Role-based Access**: Customer and admin role separation
- **Audit Logging**: Complete audit trail of all administrative actions

### Technical Features
- **Real-time Updates**: Live price updates during market hours
- **Persistent Data**: PostgreSQL database with proper migrations
- **Session Management**: Redis-backed sessions with security features
- **Rate Limiting**: Protection against abuse and brute force attacks
- **CSRF Protection**: Forms protected against cross-site request forgery

## Architecture

### Web Application (Flask Monolith)
- **Blueprints**: Modular organization (auth, market, trading, portfolio, cash, admin, common)
- **Templates**: Responsive Bootstrap-based UI
- **Forms**: WTForms with validation and CSRF protection
- **Database**: SQLAlchemy ORM with Alembic migrations

### Price Engine Worker
- **Random Walk**: Geometric Brownian motion price simulation
- **Order Processing**: Automatic execution of queued orders when market is open
- **Market Schedule**: Automatic market open/close based on configured hours
- **Position Updates**: Real-time calculation of portfolio values and P&L

### Deployment Stack
- **Web Server**: Gunicorn WSGI server behind NGINX reverse proxy
- **Process Management**: systemd services for web app and worker
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for sessions and rate limiting
- **Security**: TLS termination, security headers, and access controls

## Installation & Setup

### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- NGINX

### Quick Start (Development)

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd cx_ex
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize Database**:
   ```bash
   flask db upgrade
   python seed_db.py
   ```

4. **Start Services**:
   ```bash
   # Terminal 1: Web application
   python app.py

   # Terminal 2: Price worker
   python simple_price_worker.py

   # Terminal 3: Set market open
   python set_market_open.py true
   ```

5. **Access Application**:
   - Web Interface: http://localhost:5000
   - Admin Login: admin@example.com / admin123
   - Demo Login: demo@example.com / demo123

### Production Deployment

1. **Server Setup**:
   ```bash
   sudo bash deployment/setup_server.sh
   ```

2. **Configure Environment**:
   ```bash
   sudo cp /opt/trading-sim/.env.template /opt/trading-sim/.env
   sudo nano /opt/trading-sim/.env
   # Configure with production values
   ```

3. **Deploy Application**:
   ```bash
   # Upload code to /tmp/trading-sim
   sudo bash deployment/deploy.sh
   ```

4. **Configure Domain & SSL**:
   ```bash
   # Update NGINX configuration with your domain
   sudo nano /etc/nginx/sites-available/trading-sim
   sudo ln -s /etc/nginx/sites-available/trading-sim /etc/nginx/sites-enabled/
   sudo certbot --nginx -d your-domain.com
   sudo systemctl reload nginx
   ```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_SECRET_KEY` | - | Flask session secret (required) |
| `DATABASE_URL` | sqlite:///trading_sim.db | Database connection string |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection string |
| `MARKET_TIMEZONE` | America/New_York | Market timezone for trading hours |
| `TICK_INTERVAL_SECS` | 2 | Price update interval in seconds |
| `DEFAULT_DRIFT` | 0.0001 | Daily price drift (positive = upward bias) |
| `DEFAULT_VOLATILITY` | 0.02 | Price volatility (higher = more movement) |
| `MAX_TICK_PCT` | 0.05 | Maximum single tick movement (5%) |

### Market Hours Configuration

Market hours and holidays are configured through the admin interface:

**Trading Hours**:
- Access via Admin Dashboard → Market Hours
- Configure open/close times for each day of the week (Monday = 0, Sunday = 6)
- Default: Monday-Friday 9:30 AM - 4:00 PM EST
- Changes take effect on next scheduler check (every 30 minutes)

**Holiday Calendar**:
- Access via Admin Dashboard → Holiday Calendar
- Add/remove market holidays with specific dates
- Market remains closed on holiday dates regardless of trading hours
- Pre-configured holidays: New Year's Day, Independence Day, Christmas Day

**Emergency Controls**:
- Manual market open/close override via admin dashboard
- Sets emergency flag to distinguish from scheduled operations
- Use sparingly for maintenance or crisis situations

## API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `GET /market/stocks` - Stock listing (public view)
- `GET /market/stock/<id>` - Stock details
- `GET /market/prices` - Current price data (JSON)
- `GET /health` - Health check endpoint

### Authentication
- `GET/POST /auth/login` - User login
- `GET/POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Trading (Authenticated)
- `GET /trading/orders` - User's order history
- `GET/POST /trading/place-order` - Place new orders
- `POST /trading/cancel-order/<id>` - Cancel queued orders

### Portfolio (Authenticated)
- `GET /portfolio/` - Portfolio overview
- `GET /portfolio/history` - Trade history

### Cash Management (Authenticated)
- `GET /cash/` - Cash balance and transactions
- `GET/POST /cash/deposit` - Deposit funds
- `GET/POST /cash/withdraw` - Withdraw funds

### Admin Interface (Admin Only)
- `GET /admin/` - Admin dashboard
- `GET /admin/stocks` - Stock management
- `GET/POST /admin/stocks/create` - Create new stocks
- `GET/POST /admin/stocks/<id>/edit` - Edit stocks
- `GET /admin/market-hours` - Market hours configuration
- `GET/POST /admin/market-hours/<day>/edit` - Edit trading hours by day
- `GET /admin/holidays` - Holiday calendar management
- `GET/POST /admin/holidays/add` - Add market holidays
- `POST /admin/holidays/<id>/delete` - Delete market holidays
- `POST /admin/market-state/toggle` - Emergency market controls

## Database Schema

### Core Tables
- `users` - User accounts and authentication
- `stocks` - Tradeable securities
- `prices_live` - Current OHLC price data
- `price_ticks` - Historical price movements
- `orders` - Trade orders (queued, executed, canceled)
- `trades` - Executed transactions
- `positions` - Current user holdings
- `cash_ledger` - All cash transactions

### Configuration Tables
- `market_state` - Current market open/closed status
- `market_hours` - Trading schedule by day of week
- `market_calendar` - Holiday and special trading days
- `audit_log` - Administrative action logging

## Security Features

### Authentication & Authorization
- Password hashing with bcrypt
- Session-based authentication with Redis storage
- Role-based access control (customer/admin)
- CSRF protection on all state-changing operations

### Rate Limiting
- Login attempt limiting (5 per minute)
- Order placement limiting (10 per minute per user)
- IP-based rate limiting for sensitive endpoints

### Security Headers
- Strict Transport Security (HSTS)
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block

### Data Protection
- SQL injection protection via SQLAlchemy ORM
- Input validation and sanitization
- Secure session cookies (HttpOnly, Secure, SameSite)
- Environment variable configuration for secrets

## Monitoring & Maintenance

### Logging
- Application logs via Python logging
- System logs via systemd journal
- NGINX access and error logs
- Automatic log rotation configured

### Health Monitoring
- `/health` endpoint for application status
- systemd service monitoring and auto-restart
- Database connection health checks

### Backup Strategy
```bash
# Automated daily backups
sudo bash deployment/backup.sh

# Restore from backup
sudo bash deployment/restore.sh 20240101_120000
```

### Common Operations

**View Logs**:
```bash
# Application logs
sudo journalctl -u trading-web -u trading-worker -f

# NGINX logs
sudo tail -f /var/log/nginx/trading-sim_access.log
sudo tail -f /var/log/nginx/trading-sim_error.log
```

**Service Management**:
```bash
# Restart services
sudo systemctl restart trading-web trading-worker

# Check status
sudo systemctl status trading-web trading-worker

# View service logs
sudo journalctl -u trading-web --since "1 hour ago"
```

**Database Operations**:
```bash
# Run migrations
sudo -u www-data /opt/trading-sim/venv/bin/flask db upgrade

# Access database
sudo -u postgres psql trading_sim
```

## Development

### Running Tests
```bash
# Unit tests (if implemented)
python -m pytest tests/

# Manual testing
python -c "from app import create_app; app = create_app(); app.run(debug=True)"
```

### Code Style
- Follow PEP 8 Python style guidelines
- Use Flask-SQLAlchemy ORM for database operations
- Implement proper error handling and logging
- Use WTForms for form validation

### Database Migrations
```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade if needed
flask db downgrade
```

## Troubleshooting

### Common Issues

**Service won't start**:
- Check logs: `sudo journalctl -u trading-web -n 50`
- Verify database connection
- Check environment file permissions

**Price updates not working**:
- Ensure market is open: `python set_market_open.py true`
- Check worker service: `sudo systemctl status trading-worker`
- Verify worker logs for errors

**Database connection errors**:
- Check PostgreSQL service: `sudo systemctl status postgresql`
- Verify database credentials in `.env`
- Test connection: `psql $DATABASE_URL`

**NGINX issues**:
- Test configuration: `sudo nginx -t`
- Check error logs: `sudo tail -f /var/log/nginx/error.log`
- Verify SSL certificates are valid

## License

This project is for educational purposes only. No real money or securities are involved.

## Support

For issues and questions, please check:
1. Application logs and error messages
2. This documentation
3. System service status and logs

The simulator includes realistic market behavior but is not suitable for actual trading or financial advice.