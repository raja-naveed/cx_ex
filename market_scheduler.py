#!/usr/bin/env python3
"""
Market Scheduler - Manages market open/close based on schedule
"""

import os
import sys
from datetime import datetime, time as dt_time
import pytz

sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import MarketState, MarketHours, MarketCalendar, AuditLog

def check_and_update_market_state():
    """Check if market should be open or closed based on schedule and update state"""
    app = create_app()
    
    with app.app_context():
        # Get market timezone
        market_tz = pytz.timezone(os.environ.get('MARKET_TIMEZONE', 'America/New_York'))
        now_et = datetime.now(market_tz)
        current_date = now_et.date()
        current_time = now_et.time()
        current_weekday = now_et.weekday()  # 0=Monday, 6=Sunday
        
        # Check if today is a holiday
        holiday = MarketCalendar.query.filter_by(
            date=current_date, is_holiday=True
        ).first()
        
        should_be_open = False
        
        if not holiday and current_weekday < 5:  # Monday-Friday, not a holiday
            # Check market hours for this weekday
            market_hours = MarketHours.query.filter_by(
                day_of_week=current_weekday, is_active=True
            ).first()
            
            if market_hours:
                should_be_open = market_hours.open_time <= current_time <= market_hours.close_time
        
        # Update market state if necessary
        market_state = MarketState.get_current()
        
        if market_state.is_open != should_be_open and not market_state.emergency_close:
            old_state = market_state.is_open
            market_state.is_open = should_be_open
            market_state.last_updated = datetime.utcnow()
            db.session.commit()
            
            # Log the change
            action = 'scheduled_market_open' if should_be_open else 'scheduled_market_close'
            details = f"Market {'opened' if should_be_open else 'closed'} automatically at {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            
            AuditLog.create(
                user_id=None,
                action=action,
                resource_type='market_state',
                resource_id=None,
                details=details
            )
            
            print(f"Market state changed from {'OPEN' if old_state else 'CLOSED'} to {'OPEN' if should_be_open else 'CLOSED'}")
        else:
            current_state = 'OPEN' if market_state.is_open else 'CLOSED'
            if market_state.emergency_close:
                current_state += ' (EMERGENCY)'
            print(f"Market state unchanged: {current_state}")

if __name__ == '__main__':
    check_and_update_market_state()