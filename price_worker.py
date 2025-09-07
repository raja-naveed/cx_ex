#!/usr/bin/env python3
"""
Price Engine Worker - Random Walk Price Simulation

This worker runs continuously and:
1. Updates stock prices using a random walk algorithm during market hours
2. Processes queued orders when market is open
3. Manages market open/close schedule
"""

import os
import sys
import time
import random
import logging
from datetime import datetime, time as dt_time, date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
import pytz
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from apscheduler.schedulers.background import BackgroundScheduler

# Add the app directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.models import (
    Stock, PriceLive, PriceTick, MarketState, MarketHours, MarketCalendar,
    Order, OrderStatus, Trade, Position, CashLedger, CashTransactionType, OrderSide, db
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PriceEngine:
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.database_url = os.environ.get('DATABASE_URL', 'sqlite:///trading_sim.db')
        self.engine = create_engine(self.database_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Price simulation parameters
        self.tick_interval = float(os.environ.get('TICK_INTERVAL_SECS', '2.0'))
        self.default_drift = float(os.environ.get('DEFAULT_DRIFT', '0.0001'))
        self.default_volatility = float(os.environ.get('DEFAULT_VOLATILITY', '0.02'))
        self.max_tick_pct = float(os.environ.get('MAX_TICK_PCT', '0.05'))
        
        # Market timezone
        self.market_tz = pytz.timezone(os.environ.get('MARKET_TIMEZONE', 'America/New_York'))
        
        self.scheduler = BackgroundScheduler()
        self.running = False
        
    def start(self):
        """Start the price engine worker"""
        logger.info("Starting price engine worker...")
        self.running = True
        
        # Schedule market open/close checks
        self.scheduler.add_job(
            self.check_market_schedule,
            'cron',
            minute='*',  # Check every minute
            timezone=self.market_tz
        )
        
        # Schedule daily market reset
        self.scheduler.add_job(
            self.daily_market_reset,
            'cron',
            hour=0, minute=0,  # Midnight
            timezone=self.market_tz
        )
        
        self.scheduler.start()
        
        # Main price update loop
        try:
            while self.running:
                self.tick()
                time.sleep(self.tick_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down price engine worker...")
            self.stop()
    
    def stop(self):
        """Stop the price engine worker"""
        self.running = False
        if self.scheduler.running:
            self.scheduler.shutdown()
        self.Session.remove()
        
    def tick(self):
        """Main tick function - called every few seconds"""
        try:
            session = self.Session()
            market_state = session.query(MarketState).first()
            
            if not market_state:
                logger.warning("No market state found, creating default")
                market_state = MarketState(is_open=False)
                session.add(market_state)
                session.commit()
                return
            
            if market_state.is_open:
                # Update prices for all active stocks
                self.update_prices(session)
                
                # Process queued orders
                self.process_orders(session)
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Error in tick: {e}")
            session.rollback()
        finally:
            session.close()
    
    def update_prices(self, session):
        """Update prices using random walk for all active stocks"""
        stocks = session.query(Stock).filter_by(is_active=True).all()
        
        for stock in stocks:
            try:
                self.update_stock_price(session, stock)
            except Exception as e:
                logger.error(f"Error updating price for {stock.ticker}: {e}")
    
    def update_stock_price(self, session, stock: Stock):
        """Update price for a single stock using random walk"""
        price_live = session.query(PriceLive).filter_by(stock_id=stock.id).first()
        
        if not price_live:
            logger.info(f"Initializing price data for {stock.ticker}")
            price_live = PriceLive.initialize_from_stock(stock)
            session.add(price_live)
            session.flush()
        
        # Random walk parameters
        current_price = float(price_live.last_price)
        drift = self.default_drift
        volatility = self.default_volatility
        dt = self.tick_interval / 86400.0  # Convert seconds to fraction of day
        
        # Generate random price change
        random_factor = random.gauss(0, 1)  # Standard normal distribution
        price_change = drift * dt + volatility * random_factor * (dt ** 0.5)
        
        # Apply maximum tick limit
        max_change = current_price * self.max_tick_pct
        price_change = max(-max_change, min(max_change, price_change))
        
        # Calculate new price
        new_price = current_price * (1 + price_change)
        new_price = max(0.01, new_price)  # Minimum price of $0.01
        
        # Round to 4 decimal places
        new_price = Decimal(str(new_price)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        
        # Update live price data
        price_live.last_price = new_price
        price_live.high_price = max(price_live.high_price, new_price)
        price_live.low_price = min(price_live.low_price, new_price)
        price_live.updated_at = datetime.utcnow()
        
        # Create price tick record
        price_tick = PriceTick(
            stock_id=stock.id,
            price=new_price,
            timestamp=datetime.utcnow()
        )
        session.add(price_tick)
        
        # Clean up old price ticks (keep last 1000 per stock)
        old_ticks = session.query(PriceTick).filter_by(stock_id=stock.id)\
                          .order_by(PriceTick.timestamp.desc())\
                          .offset(1000).all()
        for old_tick in old_ticks:
            session.delete(old_tick)
    
    def process_orders(self, session):
        """Process all queued orders"""
        queued_orders = session.query(Order)\
                             .filter_by(status=OrderStatus.QUEUED)\
                             .order_by(Order.created_at).all()
        
        for order in queued_orders:
            try:
                self.execute_order(session, order)
            except Exception as e:
                logger.error(f"Error executing order {order.id}: {e}")
                order.status = OrderStatus.REJECTED
                order.updated_at = datetime.utcnow()
    
    def execute_order(self, session, order: Order):
        """Execute a single market order"""
        stock = order.stock
        price_live = session.query(PriceLive).filter_by(stock_id=stock.id).first()
        
        if not price_live:
            logger.error(f"No price data for {stock.ticker}")
            order.status = OrderStatus.REJECTED
            order.updated_at = datetime.utcnow()
            return
        
        execution_price = price_live.last_price
        user_id = order.user_id
        
        # Check if user has sufficient cash for buy orders
        if order.side == OrderSide.BUY:
            required_cash = execution_price * order.quantity
            current_cash = session.query(db.func.sum(CashLedger.amount))\
                                 .filter_by(user_id=user_id).scalar() or Decimal('0')
            
            if current_cash < required_cash:
                logger.warning(f"Insufficient funds for order {order.id}")
                order.status = OrderStatus.REJECTED
                order.updated_at = datetime.utcnow()
                return
        
        # Check if user has sufficient shares for sell orders
        if order.side == OrderSide.SELL:
            position = session.query(Position).filter_by(
                user_id=user_id, stock_id=stock.id
            ).first()
            
            if not position or position.quantity < order.quantity:
                logger.warning(f"Insufficient shares for order {order.id}")
                order.status = OrderStatus.REJECTED
                order.updated_at = datetime.utcnow()
                return
        
        # Execute the trade
        order.status = OrderStatus.EXECUTING
        order.updated_at = datetime.utcnow()
        session.flush()
        
        # Create trade record
        trade = Trade(
            order_id=order.id,
            user_id=user_id,
            stock_id=stock.id,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            executed_at=datetime.utcnow()
        )
        session.add(trade)
        
        # Update cash ledger
        cash_amount = execution_price * order.quantity
        if order.side == OrderSide.BUY:
            cash_amount = -cash_amount
            transaction_type = CashTransactionType.TRADE_BUY
        else:
            transaction_type = CashTransactionType.TRADE_SELL
        
        cash_ledger = CashLedger(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=cash_amount,
            description=f"{order.side.value.title()} {order.quantity} {stock.ticker} @ ${execution_price}",
            reference_id=f"trade_{trade.id}"
        )
        session.add(cash_ledger)
        
        # Update position
        position = session.query(Position).filter_by(
            user_id=user_id, stock_id=stock.id
        ).first()
        
        if not position:
            position = Position(user_id=user_id, stock_id=stock.id, quantity=0, avg_cost=Decimal('0'))
            session.add(position)
        
        if order.side == OrderSide.BUY:
            # Calculate new average cost
            total_cost = (position.quantity * position.avg_cost) + (order.quantity * execution_price)
            total_quantity = position.quantity + order.quantity
            position.avg_cost = total_cost / total_quantity if total_quantity > 0 else Decimal('0')
            position.quantity = total_quantity
        else:  # SELL
            position.quantity -= order.quantity
            if position.quantity == 0:
                position.avg_cost = Decimal('0')
        
        position.updated_at = datetime.utcnow()
        
        # Mark order as executed
        order.status = OrderStatus.EXECUTED
        order.updated_at = datetime.utcnow()
        
        logger.info(f"Executed order {order.id}: {order.side.value} {order.quantity} {stock.ticker} @ ${execution_price}")
    
    def check_market_schedule(self):
        """Check if market should be open or closed based on schedule"""
        try:
            session = self.Session()
            now_et = datetime.now(self.market_tz)
            current_date = now_et.date()
            current_time = now_et.time()
            current_weekday = now_et.weekday()  # 0=Monday, 6=Sunday
            
            # Check if today is a holiday
            holiday = session.query(MarketCalendar).filter_by(
                date=current_date, is_holiday=True
            ).first()
            
            should_be_open = False
            
            if not holiday and current_weekday < 5:  # Monday-Friday, not a holiday
                # Check market hours for this weekday
                market_hours = session.query(MarketHours).filter_by(
                    day_of_week=current_weekday, is_active=True
                ).first()
                
                if market_hours:
                    should_be_open = market_hours.open_time <= current_time <= market_hours.close_time
            
            # Update market state if necessary
            market_state = session.query(MarketState).first()
            if market_state and market_state.is_open != should_be_open and not market_state.emergency_close:
                market_state.is_open = should_be_open
                market_state.last_updated = datetime.utcnow()
                session.commit()
                logger.info(f"Market {'opened' if should_be_open else 'closed'} automatically")
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error checking market schedule: {e}")
    
    def daily_market_reset(self):
        """Reset daily OHLC data at market open"""
        try:
            session = self.Session()
            
            # Reset all price live data to use last price as open
            price_lives = session.query(PriceLive).all()
            for price_live in price_lives:
                price_live.open_price = price_live.last_price
                price_live.high_price = price_live.last_price
                price_live.low_price = price_live.last_price
                price_live.updated_at = datetime.utcnow()
            
            session.commit()
            session.close()
            logger.info("Daily market reset completed")
            
        except Exception as e:
            logger.error(f"Error in daily market reset: {e}")

def main():
    """Main entry point"""
    logger.info("Initializing price engine worker...")
    
    engine = PriceEngine()
    
    try:
        engine.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        engine.stop()

if __name__ == '__main__':
    main()