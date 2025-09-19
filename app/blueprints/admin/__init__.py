from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, BooleanField, SubmitField, DateField, TimeField, PasswordField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length, Email, Optional
from functools import wraps
from app import db
from app.models import Stock, PriceLive, MarketHours, MarketCalendar, MarketState, AuditLog, UserRole, User, Order, Trade, CashLedger, CandleData
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

class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Reset Password')

class UserEditForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[(UserRole.CUSTOMER.value, 'Customer'), (UserRole.ADMIN.value, 'Admin')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')

@bp.route('/')
@login_required
@admin_required
def index():
    market_state = MarketState.get_current()
    stock_count = Stock.query.filter_by(is_active=True).count()

    # User statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role=UserRole.ADMIN).count()

    # Trading statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='queued').count()
    total_trades = Trade.query.count()

    # Calculate total cash in system
    total_cash = db.session.query(db.func.sum(CashLedger.amount)).scalar() or 0

    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_trades': total_trades,
        'total_cash': float(total_cash)
    }

    return render_template('admin/index.html', market_state=market_state, stock_count=stock_count, stats=stats)

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

@bp.route('/market-hours')
@login_required
@admin_required
def market_hours():
    hours = MarketHours.query.order_by(MarketHours.day_of_week).all()
    return render_template('admin/market_hours.html', hours=hours)

@bp.route('/market-hours/<int:day>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_market_hours(day):
    market_hour = MarketHours.query.filter_by(day_of_week=day).first()
    if not market_hour:
        flash('Market hours not found', 'error')
        return redirect(url_for('admin.market_hours'))

    form = MarketHoursForm(obj=market_hour)

    if form.validate_on_submit():
        market_hour.open_time = form.open_time.data
        market_hour.close_time = form.close_time.data
        db.session.commit()

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        AuditLog.create(current_user.id, 'update_market_hours', 'market_hours', day,
                       f'Updated {days[day]} hours to {form.open_time.data}-{form.close_time.data}')

        flash(f'{days[day]} market hours updated', 'success')
        return redirect(url_for('admin.market_hours'))

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return render_template('admin/edit_market_hours.html', form=form, day=day, day_name=days[day])

@bp.route('/holidays')
@login_required
@admin_required
def holidays():
    holidays = MarketCalendar.query.order_by(MarketCalendar.date).all()
    return render_template('admin/holidays.html', holidays=holidays)

@bp.route('/holidays/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_holiday():
    form = HolidayForm()

    if form.validate_on_submit():
        existing = MarketCalendar.query.filter_by(date=form.date.data).first()
        if existing:
            flash('Holiday already exists for this date', 'error')
            return render_template('admin/add_holiday.html', form=form)

        holiday = MarketCalendar(
            date=form.date.data,
            name=form.name.data,
            is_holiday=True
        )
        db.session.add(holiday)
        db.session.commit()

        AuditLog.create(current_user.id, 'add_holiday', 'market_calendar', holiday.id,
                       f'Added holiday: {holiday.name} on {holiday.date}')

        flash(f'Holiday "{holiday.name}" added for {holiday.date}', 'success')
        return redirect(url_for('admin.holidays'))

    return render_template('admin/add_holiday.html', form=form)

@bp.route('/holidays/<int:holiday_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_holiday(holiday_id):
    holiday = MarketCalendar.query.get_or_404(holiday_id)

    AuditLog.create(current_user.id, 'delete_holiday', 'market_calendar', holiday_id,
                   f'Deleted holiday: {holiday.name} on {holiday.date}')

    db.session.delete(holiday)
    db.session.commit()

    flash(f'Holiday "{holiday.name}" deleted', 'success')
    return redirect(url_for('admin.holidays'))

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

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)

    # Get user's recent orders
    recent_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).limit(10).all()

    # Get user's positions
    positions = user.positions

    # Calculate total portfolio value
    cash_balance = user.get_cash_balance()
    portfolio_value = float(cash_balance)
    for position in positions:
        if position.quantity > 0:
            price_live = PriceLive.query.filter_by(stock_id=position.stock_id).first()
            if price_live:
                portfolio_value += float(price_live.last_price) * position.quantity
            else:
                portfolio_value += float(position.stock.initial_price) * position.quantity

    return render_template('admin/user_detail.html', user=user, recent_orders=recent_orders,
                         positions=positions, cash_balance=cash_balance, portfolio_value=portfolio_value)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        user.is_active = form.is_active.data
        db.session.commit()

        AuditLog.create(current_user.id, 'update_user', 'user', user.id, f'Updated user {user.email}')

        flash(f'User {user.email} updated successfully', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    form = PasswordResetForm()

    if form.validate_on_submit():
        if form.new_password.data != form.confirm_password.data:
            flash('Passwords do not match', 'error')
            return render_template('admin/reset_password.html', form=form, user=user)

        user.set_password(form.new_password.data)
        db.session.commit()

        AuditLog.create(current_user.id, 'reset_password', 'user', user.id, f'Reset password for user {user.email}')

        flash(f'Password reset successfully for {user.email}', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    return render_template('admin/reset_password.html', form=form, user=user)

@bp.route('/api/candles/<int:stock_id>')
@login_required
@admin_required
def get_candles_api(stock_id):
    """API endpoint to get candle data for a stock"""
    interval = request.args.get('interval', '1h')
    limit = request.args.get('limit', 100, type=int)

    # Validate interval
    valid_intervals = ['1h', '4h', '1d']
    if interval not in valid_intervals:
        return jsonify({'error': 'Invalid interval. Must be one of: ' + ', '.join(valid_intervals)}), 400

    # Validate limit
    if limit > 1000:
        limit = 1000

    # Get the stock
    stock = Stock.query.get_or_404(stock_id)

    # Get candles
    candles = CandleData.query.filter_by(
        stock_id=stock_id,
        interval=interval
    ).order_by(CandleData.timestamp_start.desc()).limit(limit).all()

    # Format response
    candle_data = []
    for candle in reversed(candles):  # Reverse to get chronological order
        candle_data.append({
            'timestamp': candle.timestamp_start.isoformat(),
            'timestamp_end': candle.timestamp_end.isoformat(),
            'open': float(candle.open_price),
            'high': float(candle.high_price),
            'low': float(candle.low_price),
            'close': float(candle.close_price),
            'volume': candle.volume
        })

    return jsonify({
        'stock': {
            'id': stock.id,
            'ticker': stock.ticker,
            'company': stock.company
        },
        'interval': interval,
        'count': len(candle_data),
        'candles': candle_data
    })

@bp.route('/candles')
@login_required
@admin_required
def candles_dashboard():
    """Dashboard to view candle data"""
    stocks = Stock.query.filter_by(is_active=True).all()

    # Get candle counts for each stock
    candle_stats = {}
    for stock in stocks:
        stats = {}
        for interval in ['1h', '4h', '1d']:
            count = CandleData.query.filter_by(stock_id=stock.id, interval=interval).count()
            latest = CandleData.get_latest_candle(stock.id, interval)
            stats[interval] = {
                'count': count,
                'latest': latest.timestamp_start.isoformat() if latest else None
            }
        candle_stats[stock.id] = stats

    return render_template('admin/candles.html', stocks=stocks, candle_stats=candle_stats)