from flask import Blueprint, render_template
from app.models import Stock, PriceLive

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('common/index.html')

@bp.route('/health')
def health():
    return {'status': 'ok'}