#!/usr/bin/env python3
"""
Simple Price Engine Worker - uses Flask app context

This worker runs continuously and updates stock prices using random walk.
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# Add the app directory to Python path
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import (
    Stock, PriceLive, PriceTick, MarketState, Order, OrderStatus, 
    Trade, Position, CashLedger, CashTransactionType, OrderSide
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimplePriceEngine:
    def __init__(self):
        self.app = create_app()
        
        # Price simulation parameters
        self.tick_interval = float(os.environ.get('TICK_INTERVAL_SECS', '2.0'))
        self.default_drift = float(os.environ.get('DEFAULT_DRIFT', '0.0001'))
        self.default_volatility = float(os.environ.get('DEFAULT_VOLATILITY', '0.02'))
        self.max_tick_pct = float(os.environ.get('MAX_TICK_PCT', '0.05'))
        
        self.running = False
        
    def start(self):
        """Start the price engine worker"""
        logger.info("Starting simple price engine worker...")
        self.running = True
        
        with self.app.app_context():
            try:
                while self.running:
                    self.tick()
                    time.sleep(self.tick_interval)
            except KeyboardInterrupt:
                logger.info("Shutting down price engine worker...")
                self.running = False
    
    def tick(self):
        """Main tick function - called every few seconds"""
        try:
            market_state = MarketState.query.first()
            
            if not market_state:
                logger.warning("No market state found, creating default")
                market_state = MarketState(is_open=False)
                db.session.add(market_state)
                db.session.commit()
                return
            
            if market_state.is_open:
                logger.info("Market is open, updating prices and processing orders...")
                # Update prices for all active stocks
                self.update_prices()
                
                # Process queued orders
                self.process_orders()
                
                db.session.commit()
            else:
                logger.info("Market is closed, no updates")
            
        except Exception as e:
            logger.error(f"Error in tick: {e}")
            db.session.rollback()
    
    def update_prices(self):
        """Update prices using random walk for all active stocks"""
        stocks = Stock.query.filter_by(is_active=True).all()
        
        for stock in stocks:
            try:
                self.update_stock_price(stock)
            except Exception as e:
                logger.error(f"Error updating price for {stock.ticker}: {e}")
    
    def update_stock_price(self, stock: Stock):
        """Update price for a single stock using random walk"""
        price_live = PriceLive.query.filter_by(stock_id=stock.id).first()
        
        if not price_live:
            logger.info(f"Initializing price data for {stock.ticker}")
            price_live = PriceLive.initialize_from_stock(stock)
        
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
        db.session.add(price_tick)
        
        logger.info(f"Updated {stock.ticker}: ${new_price}")
    
    def process_orders(self):
        """Process all queued orders"""
        queued_orders = Order.query.filter_by(status=OrderStatus.QUEUED)\
                                  .order_by(Order.created_at).all()
        
        logger.info(f"Processing {len(queued_orders)} queued orders")
        
        for order in queued_orders:
            try:
                self.execute_order(order)
            except Exception as e:
                logger.error(f"Error executing order {order.id}: {e}")
                order.status = OrderStatus.REJECTED
                order.updated_at = datetime.utcnow()
    
    def execute_order(self, order: Order):
        """Execute a single market order"""
        stock = order.stock
        price_live = PriceLive.query.filter_by(stock_id=stock.id).first()
        
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
            current_cash = db.session.query(db.func.sum(CashLedger.amount))\
                                   .filter_by(user_id=user_id).scalar() or Decimal('0')
            
            if current_cash < required_cash:
                logger.warning(f"Insufficient funds for order {order.id}")
                order.status = OrderStatus.REJECTED
                order.updated_at = datetime.utcnow()
                return
        
        # Check if user has sufficient shares for sell orders
        if order.side == OrderSide.SELL:
            position = Position.query.filter_by(
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
        db.session.add(trade)
        db.session.flush()  # Get trade ID
        
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
        db.session.add(cash_ledger)
        
        # Update position
        position = Position.query.filter_by(
            user_id=user_id, stock_id=stock.id
        ).first()
        
        if not position:
            position = Position(user_id=user_id, stock_id=stock.id, quantity=0, avg_cost=Decimal('0'))
            db.session.add(position)
        
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

def main():
    """Main entry point"""
    logger.info("Initializing simple price engine worker...")
    
    engine = SimplePriceEngine()
    engine.start()

if __name__ == '__main__':
    main()