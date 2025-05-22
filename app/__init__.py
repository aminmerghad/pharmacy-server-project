from flask import Flask
from app.config import config_by_name
from app.extensions import init_resources, container,api as apiX
from app.dataBase import db
from app.shared.infrastructure.persistence.models import *
# Import the health check blueprint
from app.api.base_routes import health_bp
# Import the webhook blueprint
from app.api.invoice.webhook_routes import webhook_bp

def create_app(config_name: str = 'development') -> Flask:
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
   
    
    # Initialize extensions
    init_resources(app)
    
    with app.app_context():       
        # Create database tables
        db.create_all()
    from app.api import order_bp, inventory_bp, auth_bp, product_bp, invoice_bp, category_bp
    apiX.register_blueprint(inventory_bp)
    apiX.register_blueprint(auth_bp)
    apiX.register_blueprint(order_bp)
    apiX.register_blueprint(product_bp)
    apiX.register_blueprint(invoice_bp)
    apiX.register_blueprint(category_bp)
    app.register_blueprint(health_bp)
    # Register the webhook blueprint
    app.register_blueprint(webhook_bp)
    return app 