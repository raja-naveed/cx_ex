import os
import sys
from datetime import time, date
from decimal import Decimal

sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import (User, Stock, PriceLive, MarketHours, MarketCalendar, 
                       MarketState, CashLedger, CashTransactionType, UserRole)

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Create admin user
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(email=admin_email, role=UserRole.ADMIN)
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f"Created admin user: {admin_email}")
        
        # Create sample customer
        customer = User.query.filter_by(email='demo@example.com').first()
        if not customer:
            customer = User(email='demo@example.com', role=UserRole.CUSTOMER)
            customer.set_password('demo123')
            db.session.add(customer)
            db.session.commit()  # Commit to get the ID
            
            # Give demo user some starting cash
            initial_cash = CashLedger(
                user_id=customer.id,
                transaction_type=CashTransactionType.DEPOSIT,
                amount=Decimal('10000.00'),
                description='Initial demo balance'
            )
            db.session.add(initial_cash)
            print("Created demo user with $10,000 starting balance")
        
        # Create market hours (Monday-Friday, 9:30 AM - 4:00 PM Eastern)
        for day in range(5):  # Monday = 0, Friday = 4
            market_hour = MarketHours.query.filter_by(day_of_week=day).first()
            if not market_hour:
                market_hour = MarketHours(
                    day_of_week=day,
                    open_time=time(9, 30),
                    close_time=time(16, 0),
                    is_active=True
                )
                db.session.add(market_hour)
        
        # Initialize market state
        market_state = MarketState.query.first()
        if not market_state:
            market_state = MarketState(is_open=False)
            db.session.add(market_state)
        
        # Create sample stocks
        sample_stocks = [
            {'ticker': 'AAPL', 'company': 'Apple Inc.', 'float_shares': 15000000000, 'initial_price': Decimal('175.25')},
            {'ticker': 'GOOGL', 'company': 'Alphabet Inc.', 'float_shares': 6000000000, 'initial_price': Decimal('2750.80')},
            {'ticker': 'MSFT', 'company': 'Microsoft Corporation', 'float_shares': 7400000000, 'initial_price': Decimal('415.50')},
            {'ticker': 'AMZN', 'company': 'Amazon.com Inc.', 'float_shares': 5200000000, 'initial_price': Decimal('3380.00')},
            {'ticker': 'TSLA', 'company': 'Tesla Inc.', 'float_shares': 3100000000, 'initial_price': Decimal('875.30')},
            {'ticker': 'NVDA', 'company': 'NVIDIA Corporation', 'float_shares': 2500000000, 'initial_price': Decimal('785.90')},
            {'ticker': 'META', 'company': 'Meta Platforms Inc.', 'float_shares': 2600000000, 'initial_price': Decimal('510.25')},
            {'ticker': 'NFLX', 'company': 'Netflix Inc.', 'float_shares': 440000000, 'initial_price': Decimal('685.75')}
        ]
        
        for stock_data in sample_stocks:
            stock = Stock.query.filter_by(ticker=stock_data['ticker']).first()
            if not stock:
                stock = Stock(**stock_data, is_active=True)
                db.session.add(stock)
                db.session.commit()
                
                # Initialize price data
                price_live = PriceLive.initialize_from_stock(stock)
                db.session.commit()
                print(f"Created stock: {stock.ticker}")
        
        # Add some sample holidays
        sample_holidays = [
            {'date': date(2024, 1, 1), 'name': "New Year's Day"},
            {'date': date(2024, 7, 4), 'name': 'Independence Day'},
            {'date': date(2024, 12, 25), 'name': 'Christmas Day'}
        ]
        
        for holiday_data in sample_holidays:
            holiday = MarketCalendar.query.filter_by(date=holiday_data['date']).first()
            if not holiday:
                holiday = MarketCalendar(**holiday_data, is_holiday=True)
                db.session.add(holiday)
        
        db.session.commit()
        print("Database seeded successfully!")
        print(f"Admin login: {admin_email} / {admin_password}")
        print("Demo login: demo@example.com / demo123")

if __name__ == '__main__':
    seed_database()