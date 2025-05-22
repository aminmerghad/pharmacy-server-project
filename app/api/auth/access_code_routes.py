from http import HTTPStatus
from typing import Dict, Any, Tuple

from flask_jwt_extended import jwt_required
from app.api.auth.schemas import (
    AccessCodeGenerationSchema, 
    AccessCodeResponseSchema, 
    AccessCodeListResponseSchema, 
    AccessCodeFilterSchema,
    AccessCodeValidationResponseSchema
)
from app.api.base_routes import BaseRoute
from app.api import auth_bp
from app.api.decorators.auth_decorator import require_admin
from app.services.auth_service.application.commands import GenerateAccessCodeCommand
from app.services.auth_service.application.queries.access_code.list_access_codes_query import ListAccessCodesQuery
from app import container

@auth_bp.route('/access-code')
class AccessCodeGeneration(BaseRoute):    
    @require_admin
    @auth_bp.doc(summary="Generate access code", description="Generate an access code for new user registration")
    @auth_bp.arguments(AccessCodeGenerationSchema)
    @auth_bp.response(HTTPStatus.CREATED, AccessCodeResponseSchema)
    def post(self, access_code_data: Dict[str, Any]):
        """Generate access code for new user registration"""
        command = GenerateAccessCodeCommand(**access_code_data)
        result = container.auth_service().generate_access_code(command)
        
        return self._success_response(
            data=result,
            message="Access code generated successfully",
            status_code=HTTPStatus.CREATED
        )

@auth_bp.route('/access-codes')
class AccessCodeList(BaseRoute):
    @require_admin
    @auth_bp.doc(summary="List access codes", description="List all access codes with optional filtering")
    @auth_bp.arguments(AccessCodeFilterSchema, location="query")
    @auth_bp.response(HTTPStatus.OK, AccessCodeListResponseSchema)
    def get(self, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        """List access codes with optional filtering"""
        query = ListAccessCodesQuery(**filter_args)
        result = container.auth_service().get_access_codes(query)
        
        return self._success_response(
            data=result,
            message=f"Retrieved {len(result['items'] if 'items' in result else [])} access codes",
            status_code=HTTPStatus.OK
        )

@auth_bp.route('/access-code/<string:access_code>')
class AccessCodeOperations(BaseRoute):
    @auth_bp.doc(summary="Validate access code", description="Check if an access code is valid")
    @auth_bp.response(HTTPStatus.OK, AccessCodeValidationResponseSchema)
    def get(self, access_code: str):
        """Validate an access code"""
        result = container.auth_service().check_access_code_validation(access_code)
        
        return self._success_response(
            data=result,
            message="Access code validation completed",
            status_code=HTTPStatus.OK
        )
    
    @require_admin
    @auth_bp.doc(summary="Delete access code", description="Delete or deactivate an access code")
    @auth_bp.response(HTTPStatus.OK, AccessCodeResponseSchema)
    def delete(self, access_code: str) :
        """Delete an access code"""
        result = container.auth_service().delete_access_code(access_code)
        
        return self._success_response(
            data=result,
            message="Access code deleted successfully",
            status_code=HTTPStatus.OK
        )
