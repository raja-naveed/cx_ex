# Trading Simulator - Component Overview

This document provides a complete overview of all components in the trading simulator system.

## Application Structure

```
cx_ex/
├── app/                          # Main Flask application
│   ├── __init__.py              # Flask app factory and configuration
│   ├── models/                  # Database models and schema
│   │   └── __init__.py         # All SQLAlchemy models
│   ├── blueprints/             # Flask blueprints for modular organization
│   │   ├── auth/               # Authentication (login, register, logout)
│   │   ├── market/             # Public market data and stock listings
│   │   ├── trading/            # Order placement and management
│   │   ├── portfolio/          # Position tracking and trade history
│   │   ├── cash/               # Cash management (deposits, withdrawals)
│   │   ├── admin/              # Administrative interface
│   │   └── common/             # Common routes (home, health check)
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html           # Base template with navigation
│   │   ├── auth/               # Authentication templates
│   │   ├── market/             # Market and stock templates
│   │   ├── trading/            # Trading interface templates
│   │   ├── portfolio/          # Portfolio management templates
│   │   ├── cash/               # Cash management templates
│   │   ├── admin/              # Admin interface templates
│   │   └── common/             # Common templates
│   └── static/                 # Static assets
│       ├── css/                # Stylesheets
│       ├── js/                 # JavaScript files
│       ├── images/             # Images and icons
│       └── robots.txt          # SEO configuration
├── migrations/                  # Alembic database migrations
├── systemd/                    # systemd service configurations
├── nginx/                      # NGINX configuration
├── deployment/                 # Deployment and maintenance scripts
├── app.py                      # Flask application entry point
├── simple_price_worker.py      # Price engine worker process
├── price_worker.py             # Advanced price worker (alternative)
├── market_scheduler.py         # Market schedule management
├── set_market_open.py          # Utility to manually control market state
├── seed_db.py                  # Database seeding script
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (local)
├── .env.example               # Environment template
├── README.md                  # Main documentation
└── COMPONENTS.md              # This file
```

## Core Components

### 1. Flask Web Application (`app/`)

**Purpose**: Main web interface for users and administrators

**Key Features**:
- Modular blueprint architecture
- Session-based authentication with Redis
- CSRF protection and rate limiting
- Responsive Bootstrap UI
- Real-time price updates via JavaScript

**Blueprints**:
- `auth`: User authentication and registration
- `market`: Public stock listings and price data
- `trading`: Order placement and management
- `portfolio`: Position tracking and P&L
- `cash`: Deposit and withdrawal management
- `admin`: Administrative controls and stock management
- `common`: Homepage and utility endpoints

### 2. Price Engine Worker (`simple_price_worker.py`)

**Purpose**: Background process for price simulation and order execution

**Key Features**:
- Random walk price algorithm (Geometric Brownian Motion)
- Configurable drift, volatility, and tick size limits
- Automatic order execution during market hours
- Position and cash ledger updates
- Real-time OHLC price tracking

**Process Flow**:
1. Check market state every 2 seconds (configurable)
2. If market is open:
   - Update all stock prices using random walk
   - Process queued orders in FIFO order
   - Update positions and cash balances
   - Create trade records and price ticks

### 3. Database Models (`app/models/__init__.py`)

**Purpose**: SQLAlchemy ORM models for all data persistence

**Core Tables**:
- `users`: User accounts with role-based access
- `stocks`: Tradeable securities with float shares
- `prices_live`: Current OHLC price data
- `price_ticks`: Historical price movements
- `orders`: Trade orders with status tracking
- `trades`: Executed transactions
- `positions`: Current user holdings with avg cost
- `cash_ledger`: All cash transactions (deposits, trades, withdrawals)
- `market_state`: Current market open/closed status
- `market_hours`: Trading schedule by day of week
- `market_calendar`: Holiday calendar
- `audit_log`: Administrative action logging

### 4. Market Scheduler (`market_scheduler.py`)

**Purpose**: Manages automatic market open/close based on schedule

**Features**:
- Timezone-aware market hours checking
- Holiday calendar integration
- Emergency override protection
- Audit logging of state changes
- Can be run via systemd timer or cron

### 5. Database Migrations (`migrations/`)

**Purpose**: Alembic-managed database schema versioning

**Usage**:
- `flask db migrate -m "Description"`: Create new migration
- `flask db upgrade`: Apply pending migrations
- `flask db downgrade`: Rollback migrations

### 6. System Services (`systemd/`)

**Purpose**: systemd service definitions for production deployment

**Services**:
- `trading-web.service`: Gunicorn WSGI server for Flask app
- `trading-worker.service`: Price engine background worker
- `trading-scheduler.service`: Market schedule checker
- `trading-scheduler.timer`: Timer for periodic schedule checks

### 7. Web Server Configuration (`nginx/`)

**Purpose**: NGINX reverse proxy with security and performance features

**Features**:
- TLS termination with modern cipher suites
- Static file serving with caching headers
- Gzip compression for dynamic content
- Security headers (HSTS, CSP, etc.)
- Rate limiting for sensitive endpoints
- Health check proxying

### 8. Deployment Scripts (`deployment/`)

**Purpose**: Production deployment and maintenance automation

**Scripts**:
- `setup_server.sh`: Initial server setup and configuration
- `deploy.sh`: Application deployment with rollback capability
- `backup.sh`: Database and application backups
- `restore.sh`: Restore from backup with safety checks

## Data Flow

### User Registration & Authentication
1. User registers via `/auth/register`
2. Password hashed with bcrypt and stored
3. User logs in via `/auth/login`
4. Session created in Redis with secure cookies
5. Role-based access enforced on protected routes

### Trading Process
1. User views stocks at `/market/stocks`
2. Real-time prices updated via JavaScript polling `/market/prices`
3. User places order via `/trading/place-order`
4. Order validation (cash for buys, shares for sells)
5. Order stored with QUEUED status
6. Price worker processes queue when market is open
7. Trade execution creates:
   - Trade record
   - Cash ledger entry
   - Position update
   - Order status change to EXECUTED

### Price Simulation
1. Price worker runs continuously
2. Every 2 seconds (configurable):
   - Check market state
   - If open, update all stock prices using random walk
   - Process any queued orders
   - Commit all changes atomically
3. Price ticks stored for historical data
4. OHLC data maintained and reset daily

### Market Schedule
1. Market scheduler runs every 30 minutes (systemd timer)
2. Checks current time against configured market hours
3. Considers weekends and holidays
4. Updates market state if needed
5. Logs all state changes for audit

## Configuration

### Environment Variables
- Database connection strings
- Redis configuration
- Market simulation parameters (drift, volatility, tick interval)
- Security settings (secret keys, session config)
- Admin user credentials

### Database Configuration
- PostgreSQL for production (persistent, ACID compliance)
- SQLite for development (simple setup)
- Connection pooling and timeout settings
- Migration management via Alembic

### Security Configuration
- HTTPS with modern TLS settings
- Secure session cookies
- CSRF protection on all forms
- Rate limiting per user/IP
- Security headers via NGINX

## Scalability Considerations

### Horizontal Scaling
- Multiple web workers behind load balancer
- Single price worker per stock (database advisory locks)
- Redis session sharing across web instances
- Read replicas for market data endpoints

### Vertical Scaling
- Increase Gunicorn worker count
- Optimize database queries and indexing
- Redis memory allocation for sessions
- NGINX worker processes and connections

### Monitoring
- Health check endpoints for load balancers
- systemd service monitoring and restart
- Log aggregation and rotation
- Database performance monitoring

## Security Features

### Authentication & Authorization
- Secure password hashing (bcrypt)
- Session-based auth with Redis
- Role-based access control
- CSRF protection on state changes

### Network Security
- HTTPS with HSTS headers
- Security headers (CSP, X-Frame-Options, etc.)
- Rate limiting on sensitive endpoints
- Firewall configuration (UFW)

### Application Security
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- Input validation and sanitization
- Secure file permissions and user isolation

## Maintenance & Operations

### Daily Operations
- Monitor service status
- Check application logs
- Verify market schedule operation
- Review audit logs

### Backup Strategy
- Daily database backups with compression
- Application file backups
- Configuration backups
- 30-day retention policy

### Disaster Recovery
- Automated backup verification
- Restore procedures with safety checks
- Service dependency management
- Rollback capabilities for deployments

## Development Workflow

### Local Development
1. Set up virtual environment
2. Install dependencies from requirements.txt
3. Configure local .env file
4. Run database migrations
5. Seed database with sample data
6. Start Flask app and price worker
7. Access at http://localhost:5000

### Deployment Process
1. Test changes locally
2. Create database migrations if needed
3. Upload code to production server
4. Run deployment script
5. Verify service health
6. Monitor logs for issues

This comprehensive system provides a realistic trading simulation environment suitable for educational purposes, with production-ready deployment and security features.