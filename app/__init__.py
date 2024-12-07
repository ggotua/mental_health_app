import os
from flask import Flask
from flask_login import LoginManager
from .db import init_db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize database
    init_db()
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
