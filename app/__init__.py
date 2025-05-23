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
            
            # Check if database exists and has tables
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                app.logger.info(f"Database already has tables: {existing_tables}")
                # Verify database connection works
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    app.logger.info("Database connection verified - using existing tables")
                except Exception as verify_error:
                    app.logger.warning(f"Database verification failed: {verify_error}")
                    # Try to recreate tables anyway
                    try:
                        db.create_all(checkfirst=True)
                        app.logger.info("Database tables recreated successfully")
                    except Exception as recreate_error:
                        app.logger.warning(f"Could not recreate tables: {recreate_error}")
                        app.logger.info("Continuing with existing database structure")
            else:
                # No tables exist, create all
                db.create_all()
                app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Failed to create database tables: {e}")
            # Try to create the directory if it doesn't exist
            import os
            if 'sqlite:///' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                # Handle absolute paths starting with '/'
                if db_path.startswith('/'):
                    db_path = db_path[1:]
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    try:
                        os.makedirs(db_dir, exist_ok=True)
                        app.logger.info(f"Created database directory: {db_dir}")
                        # Try creating tables again
                        try:
                            db.create_all(checkfirst=True)
                            app.logger.info("Database tables created successfully after directory creation")
                        except Exception as retry_error:
                            app.logger.warning(f"Could not create tables after directory creation: {retry_error}")
                            app.logger.info("Continuing anyway - database might be functional")
                    except Exception as dir_e:
                        app.logger.error(f"Failed to create database directory: {dir_e}")
                        app.logger.warning("Continuing anyway - database might be functional")
                else:
                    # Directory exists but table creation failed
                    if "already exists" in str(e).lower():
                        app.logger.info("Tables already exist - continuing with existing database")
                    else:
                        app.logger.warning(f"Database issue: {e} - continuing anyway")
            else:
                # Not SQLite, but don't crash the app
                if "already exists" in str(e).lower():
                    app.logger.info("Tables already exist - continuing with existing database")
                else:
                    app.logger.warning(f"Database initialization issue: {e} - continuing anyway")
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