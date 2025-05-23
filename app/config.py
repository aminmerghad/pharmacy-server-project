import os
from datetime import timedelta
import secrets
class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '223562326512630659986132023')
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    API_TITLE = 'Pharmacy API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.3'
    PROPAGATE_EXCEPTIONS = True
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    # APISPEC_STRICT_VALIDATION = True    

    ADMIN_INITIALIZATION_KEY = os.getenv('ADMIN_INITIALIZATION_KEY', 'your-admin-initialization-key-here')
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI= "sqlite:///pharmacy1.db"

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pharmacy_test2.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Production database URL should be set in environment variables
    # If DATABASE_URL is not set, fall back to SQLite for basic functionality
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///instance/pharmacy_prod.db'

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
} 