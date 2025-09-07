from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Position, Trade
from decimal import Decimal

bp = Blueprint('portfolio', __name__)

@bp.route('/')
@login_required
def index():
    positions = Position.query.filter_by(user_id=current_user.id).filter(Position.quantity > 0).all()
    cash_balance = current_user.get_cash_balance()
    
    total_equity = cash_balance
    for position in positions:
        total_equity += position.get_market_value()
    
    recent_trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.executed_at.desc()).limit(10).all()
    
    return render_template('portfolio/index.html', 
                         positions=positions, 
                         cash_balance=cash_balance,
                         total_equity=total_equity,
                         recent_trades=recent_trades)

@bp.route('/history')
@login_required
def history():
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.executed_at.desc()).all()
    return render_template('portfolio/history.html', trades=trades)