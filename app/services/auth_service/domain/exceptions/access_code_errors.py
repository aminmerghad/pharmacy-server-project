from http import HTTPStatus

from app.shared.domain.exceptions.common_errors import BaseAPIException, DomainError


class AccessCodeError(DomainError):
    """Base exception for access code errors"""
    def __init__(self, message: str = "Access code error"):
        super().__init__(message)


class AccessCodeNotFoundError(AccessCodeError):
    """Exception raised when an access code cannot be found"""
    def __init__(self, message: str = "Access code not found"):
        super().__init__(message)


class AccessCodeExpiredError(AccessCodeError):
    """Exception raised when an access code is expired"""
    def __init__(self, message: str = "Access code has expired"):
        super().__init__(message)


class AccessCodeUsedError(AccessCodeError):
    """Exception raised when an access code has already been used"""
    def __init__(self, message: str = "Access code has already been used"):
        super().__init__(message)


class AccessCodeInactiveError(AccessCodeError):
    """Exception raised when an access code is inactive"""
    def __init__(self, message: str = "Access code is inactive"):
        super().__init__(message)


class HealthCareCenterNotFoundForAccessCodeError(AccessCodeError):
    """Exception raised when health care center for access code cannot be found"""
    def __init__(self, message: str = "Health care center for access code not found"):
        super().__init__(message)
