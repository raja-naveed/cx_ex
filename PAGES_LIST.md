# ZEBRAT TRADING - User Pages List

This document provides a focused list of all **12 user-facing pages** in the ZEBRAT TRADING simulator application (excluding admin interface).

## 📊 **Total User Pages: 12**

---

## 🌐 **Public Pages (3 pages)**

| # | Page Name | URL Route | Description | Status |
|---|-----------|-----------|-------------|---------|
| 1 | **Homepage** | `/` | Main landing page with market overview | ✅ **COMPLETED** |
| 2 | **Market Stocks** | `/market/stocks` | Interactive stock listing with mini candlestick charts | 🔄 **PENDING** |
| 3 | **Stock Detail** | `/market/stock/<id>` | Individual stock details with full candlestick charts | 🔄 **PENDING** |

---

## 🔐 **Authentication Pages (3 pages)**

| # | Page Name | URL Route | Description | Status |
|---|-----------|-----------|-------------|---------|
| 4 | **Login** | `/auth/login` | User login form with email/password | ✅ **COMPLETED** |
| 5 | **Register** | `/auth/register` | User registration form | ✅ **COMPLETED** |
| 6 | **Logout** | `/auth/logout` | User logout functionality | ✅ **COMPLETED** |

---

## 💼 **Trading Pages (2 pages)**

| # | Page Name | URL Route | Description | Status |
|---|-----------|-----------|-------------|---------|
| 7 | **Orders** | `/trading/orders` | User's order history and status | 🔄 **PENDING** |
| 8 | **Place Order** | `/trading/place-order` | Buy/sell order placement form | 🔄 **PENDING** |

---

## 📈 **Portfolio Pages (2 pages)**

| # | Page Name | URL Route | Description | Status |
|---|-----------|-----------|-------------|---------|
| 9 | **Portfolio Overview** | `/portfolio/` | Portfolio summary with positions, P&L, and cash balance | 🔄 **PENDING** |
| 10 | **Trade History** | `/portfolio/history` | Complete trading history and executed trades | 🔄 **PENDING** |

---

## 💰 **Cash Management Pages (2 pages)**

| # | Page Name | URL Route | Description | Status |
|---|-----------|-----------|-------------|---------|
| 11 | **Cash Dashboard** | `/cash/` | Cash balance and transaction history | 🔄 **PENDING** |
| 12 | **Deposit/Withdraw** | `/cash/deposit`, `/cash/withdraw` | Cash management forms | 🔄 **PENDING** |

---

## 🔧 **User API Endpoints**

### **Public Endpoints**
- **Health Check** (`/health`) - Application status endpoint
- **Market Prices** (`/market/prices`) - Current price data (JSON)
- **Stock Candles API** (`/market/api/stock/<id>/candles`) - Historical OHLC data (JSON)

### **Authenticated Endpoints**
- **Trading Orders** (`/trading/orders`) - User's order history
- **Place Order** (`/trading/place-order`) - Place new orders
- **Cancel Order** (`/trading/cancel-order/<id>`) - Cancel queued orders
- **Portfolio Overview** (`/portfolio/`) - Portfolio summary
- **Trade History** (`/portfolio/history`) - Trading history
- **Cash Management** (`/cash/`) - Cash balance and transactions

---

## 🎯 **Quick Access Credentials**

### **Demo User Access**
- **Email**: demo@example.com
- **Password**: demo123
- **Access**: All user pages (1-12)

### **Admin Access** (Not in scope)
- **Email**: admin@example.com
- **Password**: admin123
- **Access**: Admin interface (excluded from user scope)

---

## 🚀 **Application Status**

✅ **Application is RUNNING**  
🌐 **URL**: http://localhost:5000  
🗄️ **Database**: SQLite (initialized with sample data)  
📊 **Sample Data**: 150 stocks, 2 users, market hours configured  

---

## 📁 **User Template Files Structure**

The user interface uses **8 template files** organized across 5 directories:

- **Auth Templates** (2 files): Login and registration
- **Market Templates** (2 files): Stock listing and details
- **Trading Templates** (2 files): Orders and order placement
- **Portfolio Templates** (2 files): Overview and history
- **Cash Templates** (2 files): Dashboard and cash management
- **Common Templates** (1 file): Base template and homepage

---

## 🎨 **Design System**

### **Theme**
- **Primary**: Dark theme with emerald green accents
- **Typography**: Inter font family
- **Components**: Modern cards, buttons, and forms
- **Layout**: Responsive grid system

### **Completed Pages**
- ✅ **Homepage**: Modern dark theme with hero section, features grid, and trading preview
- ✅ **Login Page**: Modern dark theme with animated background, interactive form controls, and demo account
- ✅ **Register Page**: Modern dark theme with terms agreement, password validation, and benefits showcase

### **Pending**
- 🔄 **Market Pages**: Interactive stock listings and detail views
- 🔄 **Trading Pages**: Order management and placement forms
- 🔄 **Portfolio Pages**: Dashboard and history views
- 🔄 **Cash Pages**: Balance and transaction management

---

*Last Updated: September 30, 2025*  
*User Pages: 12 | Status: 3 Completed, 9 Pending*
