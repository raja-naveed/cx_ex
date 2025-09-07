import os
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///trading_sim.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    redis_client = redis.from_url(redis_url)
    
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_client
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.market import bp as market_bp
    from app.blueprints.trading import bp as trading_bp
    from app.blueprints.portfolio import bp as portfolio_bp
    from app.blueprints.cash import bp as cash_bp
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.common import bp as common_bp
    
    app.register_blueprint(common_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(market_bp, url_prefix='/market')
    app.register_blueprint(trading_bp, url_prefix='/trading')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    app.register_blueprint(cash_bp, url_prefix='/cash')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.models import MarketState
    
    @app.context_processor
    def inject_market_state():
        market_state = MarketState.get_current()
        return {'market_state': market_state}
    
    # Add abs function to Jinja2 template environment
    app.jinja_env.globals['abs'] = abs
    
    return app