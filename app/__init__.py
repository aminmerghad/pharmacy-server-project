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
        try:
            # Log database URI for debugging (mask sensitive parts)
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            if 'password' in db_uri.lower():
                # Mask password in logs
                masked_uri = db_uri.split('@')[0].split('://')[0] + '://***:***@' + db_uri.split('@')[1] if '@' in db_uri else db_uri
                app.logger.info(f"Database URI: {masked_uri}")
            else:
                app.logger.info(f"Database URI: {db_uri}")
            
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Failed to create database tables: {e}")
            # Try to create the directory if it doesn't exist
            import os
            if 'sqlite:///' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    try:
                        os.makedirs(db_dir, exist_ok=True)
                        app.logger.info(f"Created database directory: {db_dir}")
                        db.create_all()
                        app.logger.info("Database tables created successfully after directory creation")
                    except Exception as dir_e:
                        app.logger.error(f"Failed to create database directory: {dir_e}")
                        raise e
                else:
                    raise e
            else:
                raise e
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