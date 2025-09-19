from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app import db, limiter
from app.models import Stock, Order, OrderSide, OrderStatus, PriceLive
import uuid

bp = Blueprint('trading', __name__)

class OrderForm(FlaskForm):
    stock_id = SelectField('Stock', coerce=int, validators=[DataRequired()])
    side = SelectField('Side', choices=[(OrderSide.BUY.value, 'Buy'), (OrderSide.SELL.value, 'Sell')], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    submit = SubmitField('Place Order')

@bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('trading/orders.html', orders=user_orders)

@bp.route('/place-order', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def place_order():
    form = OrderForm()
    stocks = Stock.query.filter_by(is_active=True).all()
    form.stock_id.choices = [(s.id, f"{s.ticker} - {s.company}") for s in stocks]

    # Get current prices for all stocks
    stock_prices = {}
    for stock in stocks:
        price_live = PriceLive.query.filter_by(stock_id=stock.id).first()
        if price_live:
            stock_prices[stock.id] = float(price_live.last_price)
        else:
            stock_prices[stock.id] = float(stock.initial_price)

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            stock_id=form.stock_id.data,
            side=OrderSide(form.side.data),
            quantity=form.quantity.data,
            idempotency_key=str(uuid.uuid4())
        )
        db.session.add(order)
        db.session.commit()

        flash('Order placed successfully', 'success')
        return redirect(url_for('trading.orders'))

    return render_template('trading/place_order.html', form=form, stock_prices=stock_prices)

@bp.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if order.status != OrderStatus.QUEUED:
        flash('Order cannot be canceled', 'error')
    else:
        order.status = OrderStatus.CANCELED
        db.session.commit()
        flash('Order canceled', 'success')
    
    return redirect(url_for('trading.orders'))