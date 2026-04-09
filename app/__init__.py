import os
from flask import Flask, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['PORT'] = int(os.environ.get('PORT', 8080))
    
    limiter.init_app(app)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from app.main import main_bp
    from app.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'version': '3.0.0'}
    
    return app
