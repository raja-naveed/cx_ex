#!/usr/bin/env python3
"""
Simple script to set market open/closed for testing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import MarketState

def set_market_open(is_open=True):
    app = create_app()
    
    with app.app_context():
        market_state = MarketState.get_current()
        market_state.is_open = is_open
        db.session.commit()
        print(f"Market set to {'OPEN' if is_open else 'CLOSED'}")

if __name__ == '__main__':
    is_open = len(sys.argv) > 1 and sys.argv[1].lower() in ['true', '1', 'open', 'yes']
    set_market_open(is_open)