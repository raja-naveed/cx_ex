from flask import Blueprint, render_template, jsonify, request
from app.models import Stock, PriceLive, CandleData

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

@bp.route('/api/stock/<int:stock_id>/candles')
def stock_candles_api(stock_id):
    """API endpoint to get candlestick data for a stock"""
    interval = request.args.get('interval', '1h')
    limit = request.args.get('limit', 100, type=int)

    # Validate interval
    valid_intervals = ['1h', '4h', '1d']
    if interval not in valid_intervals:
        return jsonify({'error': 'Invalid interval. Must be one of: ' + ', '.join(valid_intervals)}), 400

    # Validate limit
    if limit > 500:  # Reasonable limit for charts
        limit = 500

    # Get the stock
    stock = Stock.query.get_or_404(stock_id)

    # Get candles
    candles = CandleData.query.filter_by(
        stock_id=stock_id,
        interval=interval
    ).order_by(CandleData.timestamp_start.desc()).limit(limit).all()

    # Format for charting libraries (reverse to get chronological order)
    candle_data = []
    for candle in reversed(candles):
        candle_data.append({
            'x': int(candle.timestamp_start.timestamp() * 1000),  # Unix timestamp in milliseconds
            'time': candle.timestamp_start.isoformat(),
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
        'data': candle_data
    })