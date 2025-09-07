from flask import Blueprint, render_template, jsonify
from app.models import Stock, PriceLive

bp = Blueprint('market', __name__)

@bp.route('/stocks')
def stocks():
    stocks = Stock.query.filter_by(is_active=True).all()
    return render_template('market/stocks.html', stocks=stocks)

@bp.route('/stock/<int:stock_id>')
def stock_detail(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    return render_template('market/stock_detail.html', stock=stock)

@bp.route('/prices')
def prices():
    prices = {}
    price_data = PriceLive.query.all()
    for price in price_data:
        prices[price.stock_id] = {
            'last_price': float(price.last_price),
            'open_price': float(price.open_price),
            'high_price': float(price.high_price),
            'low_price': float(price.low_price),
            'change': float(price.last_price - price.open_price)
        }
    return jsonify(prices)