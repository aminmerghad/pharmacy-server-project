from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from app.container import Container
from app.dataBase import db
from flask_smorest import Api

ma = Marshmallow()
jwt = JWTManager()

container = Container()
api = Api()

# @api.errorhandler(Exception)
# def handle_global_error(error):
#     """
#     General handler for all exceptions.
#     """
#     status_code = getattr(error, "code", 500)  # Default to 500 if no code is found
#     description = getattr(error, "description", "An unexpected error occurred")

#     if isinstance(description, dict):  # Check if description is a dictionary
#         response = jsonify(description)
#     else:
#         response = jsonify({
#             "code": status_code,
#             "status": "Error",
#             "message": str(description)
#         })
#     response.status_code = status_code
#     return response
def init_resources(app: Flask):
    """Initialize Flask extensions"""
    # Initialize database
    db.init_app(app)
    
    # Initialize other extensions
    ma.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    # Initialize container resources
    container.init_acl()
    
    # Initialize event bus and ensure it's ready for event publishing/subscribing
    event_bus = container.event_bus()
    if event_bus:
        event_bus.init()
    
    # Store initialized resources in app context to prevent garbage collection
    if not hasattr(app, 'extensions_data'):
        app.extensions_data = {}
    
    app.extensions_data['event_bus'] = event_bus

    
    


