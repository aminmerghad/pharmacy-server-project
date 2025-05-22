from http import HTTPStatus
from typing import Any,Dict
from flask import jsonify
# from app.middleware.sanitizer import sanitize_input

class APIResponse:
    """Standard API response helper"""
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = HTTPStatus.OK) -> tuple:
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        return jsonify(response)

    @staticmethod
    def error(message: str = "Error", data: Dict = None, errors: Dict = None, status_code: int = HTTPStatus.BAD_REQUEST) -> tuple:
        response = {
            "data":data,
            "success": False,
            "message": message,
            "errors": errors
        }
        return jsonify(response), status_code
    @staticmethod
    def additional_claims(user):
        role =user.role
        access_code = user.access_codes.code
        health_center = user.health_care_center
        return {"role": role, 
                         'user': {
                            'user_id': str(user.id),
                            'full_name': user.name, 
                            'username':user.username,
                            'email': user.email, 
                            'access_codes':access_code,                            
                        },
                        'health_care_center':{
                            'health_care_center_id':str(health_center.id),
                            'health_care_center_name':health_center.name,
                            'health_care_center_address':health_center.address.street, 
                        }
                        }  
