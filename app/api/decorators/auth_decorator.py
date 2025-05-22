from functools import wraps
from uuid import UUID
from flask import request, jsonify
from http import HTTPStatus
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.services.auth_service.infrastructure.persistence.models.user_model import UserModel

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Authentication required"
            }), HTTPStatus.UNAUTHORIZED
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            user = UserModel.query.get(UUID(current_user))
            if not user.is_admin:
                return jsonify({
                    "success": False,
                    "message": "Admin privileges required"
                }), HTTPStatus.FORBIDDEN
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return jsonify({
                "success": False,
                "message": "Authentication required"
            }), HTTPStatus.UNAUTHORIZED
    return decorated 