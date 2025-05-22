from flask import jsonify
from flask_smorest import Blueprint

# Create Blueprints
inventory_bp = Blueprint('inventory', __name__,url_prefix='/inventory',description='Inventory API')
auth_bp = Blueprint('auth', __name__,url_prefix='/auth',description='Authentication API')
order_bp = Blueprint('order', __name__,url_prefix='/order',description='Order API')
product_bp = Blueprint('product', __name__,url_prefix='/api/products',description='Product API')
invoice_bp = Blueprint('invoice', __name__,url_prefix='/invoice',description='Invoice API')
category_bp = Blueprint('category', __name__,url_prefix='/api/categories',description='Category API')


# Import routes after Blueprint creation to avoid circular imports
from app.api.shop.inventory_routes import *
from app.api.auth.auth_routes import *
from app.api.auth.access_code_routes import *
from app.api.auth.health_care_center import *

from app.api.order.order_routes import *
from app.api.shop.stock_routes import *
from app.api.product.routes import *
from app.api.invoice.invoice_routes import *
from app.api.category.routes import *
