# ZEBRAT TRADING - Complete Pages List

This document provides a comprehensive list of all 25 pages available in the ZEBRAT TRADING simulator application.

## 📊 **Total Pages: 25**

---

## 🌐 **Public Pages (3 pages)**

| # | Page Name | URL Route | Description |
|---|-----------|-----------|-------------|
| 1 | **Homepage** | `/` | Main landing page with market overview ✅ **COMPLETED** |
| 2 | **Market Stocks** | `/market/stocks` | Interactive stock listing with mini candlestick charts |
| 3 | **Stock Detail** | `/market/stock/<id>` | Individual stock details with full candlestick charts |

---

## 🔐 **Authentication Pages (3 pages)**

| # | Page Name | URL Route | Description |
|---|-----------|-----------|-------------|
| 4 | **Login** | `/auth/login` | User login form with email/password |
| 5 | **Register** | `/auth/register` | User registration form |
| 6 | **Logout** | `/auth/logout` | User logout functionality |

---

## 💼 **Trading Pages (2 pages)**

| # | Page Name | URL Route | Description |
|---|-----------|-----------|-------------|
| 7 | **Orders** | `/trading/orders` | User's order history and status |
| 8 | **Place Order** | `/trading/place-order` | Buy/sell order placement form |

---

## 📈 **Portfolio Pages (2 pages)**

| # | Page Name | URL Route | Description |
|---|-----------|-----------|-------------|
| 9 | **Portfolio Overview** | `/portfolio/` | Portfolio summary with positions, P&L, and cash balance |
| 10 | **Trade History** | `/portfolio/history` | Complete trading history and executed trades |

---

## 💰 **Cash Management Pages (3 pages)**

| # | Page Name | URL Route | Description |
|---|-----------|-----------|-------------|
| 11 | **Cash Dashboard** | `/cash/` | Cash balance and transaction history |
| 12 | **Deposit Funds** | `/cash/deposit` | Deposit funds form |
| 13 | **Withdraw Funds** | `/cash/withdraw` | Withdraw funds form |

---

## 👨‍💼 **Admin Interface Pages (12 pages)**

| # | Page Name | URL Route | Description |
|---|-----------|-----------|-------------|
| 14 | **Admin Dashboard** | `/admin/` | Enhanced admin dashboard with live statistics |
| 15 | **Stocks Management** | `/admin/stocks` | List and manage all stocks |
| 16 | **Create Stock** | `/admin/stocks/create` | Form to create new stocks |
| 17 | **Edit Stock** | `/admin/stocks/<id>/edit` | Form to edit existing stocks |
| 18 | **Users Management** | `/admin/users` | User list with pagination |
| 19 | **User Detail** | `/admin/users/<id>` | Individual user details and portfolio info |
| 20 | **Edit User** | `/admin/users/<id>/edit` | Form to edit user details and permissions |
| 21 | **Reset Password** | `/admin/users/<id>/reset-password` | Password reset form for users |
| 22 | **Market Hours** | `/admin/market-hours` | Trading hours configuration by day |
| 23 | **Edit Market Hours** | `/admin/market-hours/<day>/edit` | Edit trading hours for specific day |
| 24 | **Holidays Management** | `/admin/holidays` | Holiday calendar management |
| 25 | **Add Holiday** | `/admin/holidays/add` | Form to add market holidays |

---

## 🔧 **Additional Features & API Endpoints**

### **Admin Extensions**
- **Candles Dashboard** (`/admin/candles`) - Candle data dashboard and statistics
- **Market State Toggle** (`/admin/market-state/toggle`) - Emergency market controls

### **API Endpoints**
- **Health Check** (`/health`) - Application status endpoint
- **Market Prices** (`/market/prices`) - Current price data (JSON)
- **Stock Candles API** (`/market/api/stock/<id>/candles`) - Historical OHLC data (JSON)
- **Admin Candles API** (`/admin/api/candles/<stock_id>`) - Admin candle data API

---

## 🎯 **Quick Access Credentials**

### **Admin Access**
- **Email**: admin@example.com
- **Password**: admin123
- **Access**: Full admin interface (pages 14-25)

### **Demo User Access**
- **Email**: demo@example.com
- **Password**: demo123
- **Access**: Customer interface (pages 1-13)

---

## 🚀 **Application Status**

✅ **Application is RUNNING**  
🌐 **URL**: http://localhost:5000  
🗄️ **Database**: SQLite (initialized with sample data)  
📊 **Sample Data**: 150 stocks, 2 users, market hours configured  

---

## 📁 **Template Files Structure**

The application uses **21 template files** organized across 7 directories:

- **Admin Templates** (13 files): Complete admin interface
- **Auth Templates** (2 files): Login and registration
- **Market Templates** (2 files): Stock listing and details
- **Trading Templates** (2 files): Orders and order placement
- **Portfolio Templates** (2 files): Overview and history
- **Cash Templates** (3 files): Dashboard, deposit, withdraw
- **Common Templates** (1 file): Base template and homepage

---

*Last Updated: September 30, 2025*  
*Total Pages: 25 | Total Templates: 21 | Status: Fully Operational*
