from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Index, UniqueConstraint
from app import db

class UserRole(Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class OrderStatus(Enum):
    QUEUED = "queued"
    EXECUTING = "executing"
    EXECUTED = "executed"
    CANCELED = "canceled"
    REJECTED = "rejected"

class OrderType(Enum):
    MARKET = "market"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class CashTransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRADE_BUY = "trade_buy"
    TRADE_SELL = "trade_sell"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    trades = db.relationship('Trade', backref='user', lazy=True)
    positions = db.relationship('Position', backref='user', lazy=True)
    cash_ledger = db.relationship('CashLedger', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_cash_balance(self):
        result = db.session.query(db.func.sum(CashLedger.amount)).filter_by(user_id=self.id).scalar()
        return result or Decimal('0.00')
    
    def is_admin(self):
        return self.role == UserRole.ADMIN

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    company = db.Column(db.String(255), nullable=False)
    float_shares = db.Column(db.BigInteger, nullable=False)
    initial_price = db.Column(db.Numeric(10, 4), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    prices_live = db.relationship('PriceLive', backref='stock', uselist=False)
    price_ticks = db.relationship('PriceTick', backref='stock', lazy=True)
    orders = db.relationship('Order', backref='stock', lazy=True)
    trades = db.relationship('Trade', backref='stock', lazy=True)
    positions = db.relationship('Position', backref='stock', lazy=True)
    
    def get_market_cap(self):
        if self.prices_live and self.prices_live.last_price:
            return self.float_shares * self.prices_live.last_price
        return self.float_shares * self.initial_price

class PriceLive(db.Model):
    __tablename__ = 'prices_live'
    
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
    last_price = db.Column(db.Numeric(10, 4), nullable=False)
    open_price = db.Column(db.Numeric(10, 4), nullable=False)
    high_price = db.Column(db.Numeric(10, 4), nullable=False)
    low_price = db.Column(db.Numeric(10, 4), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    @classmethod
    def initialize_from_stock(cls, stock):
        price_live = cls(
            stock_id=stock.id,
            last_price=stock.initial_price,
            open_price=stock.initial_price,
            high_price=stock.initial_price,
            low_price=stock.initial_price
        )
        db.session.add(price_live)
        return price_live

class PriceTick(db.Model):
    __tablename__ = 'price_ticks'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    price = db.Column(db.Numeric(10, 4), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (Index('ix_price_ticks_stock_timestamp', 'stock_id', 'timestamp'),)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    order_type = db.Column(db.Enum(OrderType), nullable=False, default=OrderType.MARKET)
    side = db.Column(db.Enum(OrderSide), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.QUEUED)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    idempotency_key = db.Column(db.String(255), unique=True, nullable=False)
    
    trades = db.relationship('Trade', backref='order', lazy=True)
    
    __table_args__ = (Index('ix_orders_status_created', 'status', 'created_at'),)

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    side = db.Column(db.Enum(OrderSide), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 4), nullable=False)
    executed_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    @property
    def total_value(self):
        return self.quantity * self.price

class Position(db.Model):
    __tablename__ = 'positions'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    avg_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_market_value(self):
        if self.stock.prices_live:
            return self.quantity * self.stock.prices_live.last_price
        return Decimal('0.00')
    
    def get_unrealized_pnl(self):
        market_value = self.get_market_value()
        cost_basis = self.quantity * self.avg_cost
        return market_value - cost_basis

class CashLedger(db.Model):
    __tablename__ = 'cash_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.Enum(CashTransactionType), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.String(255))
    reference_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (Index('ix_cash_ledger_user_created', 'user_id', 'created_at'),)

class MarketHours(db.Model):
    __tablename__ = 'market_hours'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (UniqueConstraint('day_of_week'),)

class MarketCalendar(db.Model):
    __tablename__ = 'market_calendar'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    is_holiday = db.Column(db.Boolean, default=True)

class MarketState(db.Model):
    __tablename__ = 'market_state'
    
    id = db.Column(db.Integer, primary_key=True)
    is_open = db.Column(db.Boolean, nullable=False, default=False)
    last_updated = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    emergency_close = db.Column(db.Boolean, default=False)
    
    @classmethod
    def get_current(cls):
        state = cls.query.first()
        if not state:
            state = cls(is_open=False)
            db.session.add(state)
            db.session.commit()
        return state
    
    @classmethod
    def set_market_open(cls, is_open, emergency=False):
        state = cls.get_current()
        state.is_open = is_open
        state.emergency_close = emergency
        state.last_updated = datetime.utcnow()
        db.session.commit()
        return state

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(100))
    resource_id = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (Index('ix_audit_log_created', 'created_at'),)
    
    @classmethod
    def create(cls, user_id, action, resource_type=None, resource_id=None, details=None):
        log = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log