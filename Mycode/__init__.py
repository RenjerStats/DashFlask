from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        from .dashboard import init_dashboard
        from . import routes
        
        app = init_dashboard(app)
        
        return app