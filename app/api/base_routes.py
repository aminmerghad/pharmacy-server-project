from typing import Any
from flask.views import MethodView
from http import HTTPStatus
from flask_smorest import abort
from werkzeug.exceptions import UnprocessableEntity
from app.shared.domain.exceptions.common_errors import BaseAPIException
from flask import Blueprint, jsonify
from flask_smorest import Api
from app.shared.utils.api_response import APIResponse
from flask import current_app
import datetime

class BaseRoute(MethodView):
    """Base route class with common functionality for all routes"""
    

    def dispatch_request(self, *args: Any, **kwargs: Any) -> Any:
        """Override dispatch_request to add global exception handling"""
        try:
            return super().dispatch_request(*args, **kwargs)
        except BaseAPIException as e:  
            
            self._error_response(
                status_code=e.status_code,
                message=e.message,
                errors=e.errors
            )
        except UnprocessableEntity as e:
            raise e            
        except Exception as e: 
            self._error_response(
                message="An unexpected error occurred",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                errors=str(e)
            )
    
    def _success_response(self, data=None, message="Success", status_code=HTTPStatus.OK):
        response = {
            "code": status_code,
            "message": message,
            "data": data
        }
        return response, status_code

    def _error_response(self, 
                       message: str = "Error occurred", 
                       status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
                       errors: Any = None) -> None:   
        if errors is None:
             abort(status_code, message=message)
        abort(status_code, message=message,  errors=errors)
        

# Add health check blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('/')
def health_check():
    """Health check endpoint to verify server status"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": getattr(current_app, 'version', '1.0.0'),
        "services": {
            "auth": "available",
            "product": "available",
            "order": "available",
            "inventory": "available"
        }
    }
    
    response = {
        "code": HTTPStatus.OK,
        "message": "Server is running correctly",
        "data": health_data
    }
    
    return jsonify(response), HTTPStatus.OK
        
