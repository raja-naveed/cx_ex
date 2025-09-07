from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, BooleanField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, NumberRange, Length
from functools import wraps
from app import db
from app.models import Stock, PriceLive, MarketHours, MarketCalendar, MarketState, AuditLog, UserRole
from decimal import Decimal

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

class StockForm(FlaskForm):
    ticker = StringField('Ticker', validators=[DataRequired(), Length(max=10)])
    company = StringField('Company', validators=[DataRequired(), Length(max=255)])
    float_shares = IntegerField('Float Shares', validators=[DataRequired(), NumberRange(min=1)])
    initial_price = DecimalField('Initial Price', validators=[DataRequired(), NumberRange(min=0.01)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class MarketHoursForm(FlaskForm):
    open_time = TimeField('Open Time', validators=[DataRequired()])
    close_time = TimeField('Close Time', validators=[DataRequired()])
    submit = SubmitField('Save')

class HolidayForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    name = StringField('Holiday Name', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Add Holiday')

@bp.route('/')
@login_required
@admin_required
def index():
    market_state = MarketState.get_current()
    stock_count = Stock.query.filter_by(is_active=True).count()
    return render_template('admin/index.html', market_state=market_state, stock_count=stock_count)

@bp.route('/stocks')
@login_required
@admin_required
def stocks():
    stocks = Stock.query.order_by(Stock.ticker).all()
    return render_template('admin/stocks.html', stocks=stocks)

@bp.route('/stocks/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_stock():
    form = StockForm()
    form.is_active.data = True
    
    if form.validate_on_submit():
        if Stock.query.filter_by(ticker=form.ticker.data.upper()).first():
            flash('Ticker already exists', 'error')
            return render_template('admin/create_stock.html', form=form)
        
        stock = Stock(
            ticker=form.ticker.data.upper(),
            company=form.company.data,
            float_shares=form.float_shares.data,
            initial_price=form.initial_price.data,
            is_active=form.is_active.data
        )
        db.session.add(stock)
        db.session.commit()
        
        PriceLive.initialize_from_stock(stock)
        db.session.commit()
        
        AuditLog.create(current_user.id, 'create_stock', 'stock', stock.id, f'Created stock {stock.ticker}')
        
        flash(f'Stock {stock.ticker} created', 'success')
        return redirect(url_for('admin.stocks'))
    
    return render_template('admin/create_stock.html', form=form)

@bp.route('/stocks/<int:stock_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    form = StockForm(obj=stock)
    
    if form.validate_on_submit():
        stock.ticker = form.ticker.data.upper()
        stock.company = form.company.data
        stock.float_shares = form.float_shares.data
        stock.initial_price = form.initial_price.data
        stock.is_active = form.is_active.data
        db.session.commit()
        
        AuditLog.create(current_user.id, 'update_stock', 'stock', stock.id, f'Updated stock {stock.ticker}')
        
        flash(f'Stock {stock.ticker} updated', 'success')
        return redirect(url_for('admin.stocks'))
    
    return render_template('admin/edit_stock.html', form=form, stock=stock)

@bp.route('/market-state/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_market():
    current_state = MarketState.get_current()
    new_state = not current_state.is_open
    MarketState.set_market_open(new_state, emergency=True)
    
    action = 'emergency_open' if new_state else 'emergency_close'
    AuditLog.create(current_user.id, action, 'market_state', None, f'Market {"opened" if new_state else "closed"} manually')
    
    flash(f'Market {"opened" if new_state else "closed"}', 'success')
    return redirect(url_for('admin.index'))