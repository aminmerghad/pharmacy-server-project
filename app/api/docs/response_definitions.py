from http import HTTPStatus
from app.api.auth.schemas import (
    AdminRegistrationResponseSchema, 
    UserResponseSchema,
    LogInResponseSchema,
    AccessCodeResponseSchema
)
from app.shared.domain.schema.common_errors import ErrorResponseSchema

class ApiResponseDefinition:
    """API Response definitions for documentation"""
    
    @staticmethod
    def get_admin_registration_responses():
        return {
            HTTPStatus.CREATED.value: {
                'description': 'Admin registered successfully',
                'schema': AdminRegistrationResponseSchema
            },
            HTTPStatus.BAD_REQUEST.value: {
                'description': 'Invalid input data',
                'schema': ErrorResponseSchema
            },
            HTTPStatus.UNAUTHORIZED.value: {
                'description': 'Invalid initialization key',
                'schema': ErrorResponseSchema
            },
            HTTPStatus.CONFLICT.value: {
                'description': 'Admin account already exists',
                'schema': ErrorResponseSchema
            }
        }

    @staticmethod
    def get_user_registration_responses():
        return {
            HTTPStatus.CREATED.value: {
                'description': 'User registered successfully',
                'schema': UserResponseSchema
            },
            HTTPStatus.BAD_REQUEST.value: {
                'description': 'Invalid input data',
                'schema': ErrorResponseSchema
            },
            HTTPStatus.UNPROCESSABLE_ENTITY.value: {
                'description': 'Invalid or expired access code',
                'schema': ErrorResponseSchema
            }
        }

    @staticmethod
    def get_login_responses():
        return {
            HTTPStatus.OK.value: {
                'description': 'Login successful',
                'schema': LogInResponseSchema
            },
            HTTPStatus.UNAUTHORIZED.value: {
                'description': 'Invalid credentials',
                'schema': ErrorResponseSchema
            }
        }

    @staticmethod
    def get_access_code_responses():
        return {
            HTTPStatus.CREATED.value: {
                'description': 'Access code generated successfully',
                'schema': AccessCodeResponseSchema
            },
            HTTPStatus.UNAUTHORIZED.value: {
                'description': 'Authentication required',
                'schema': ErrorResponseSchema
            },
            HTTPStatus.FORBIDDEN.value: {
                'description': 'Admin privileges required',
                'schema': ErrorResponseSchema
            }
        } 