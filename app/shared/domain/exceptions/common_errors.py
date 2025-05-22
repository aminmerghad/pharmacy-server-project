
from http import HTTPStatus
from typing import Optional


class BaseAPIException(Exception):
    """Base exception for all API errors"""
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    errors: Optional[dict] = None

    def __init__(self, message: Optional[str] = None, status_code: Optional[HTTPStatus] = None) -> None:
        self.message = message or "An unexpected error occurred"
        if status_code:
            self.status_code = status_code
        
        super().__init__(self.message)

class InitializeComponentsError(BaseAPIException):
    """Raised when initialization of inventory components fails."""
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "INITIALIZATION_ERROR"

class ValidationError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
    error_code: str = "VALIDATION_ERROR"


class DomainError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
    error_code: str = "DOMAIN_ERROR"

class ResourceNotFoundError(BaseAPIException):
    """Raised when a requested resource cannot be found."""
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND
    error_code: str = "RESOURCE_NOT_FOUND" 
