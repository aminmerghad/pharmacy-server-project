from http import HTTPStatus

from app.shared.domain.exceptions.common_errors import BaseAPIException

class AuthenticationError(BaseAPIException):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"

class InvalidCredentialsError(AuthenticationError):
    error_code = "INVALID_CREDENTIALS"

class UserNotFoundError(BaseAPIException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "USER_NOT_FOUND"

class UserAlreadyExistsError(BaseAPIException):
    status_code = HTTPStatus.CONFLICT
    error_code = "USER_EXISTS"

class InvalidInitializationKey(BaseAPIException):
    status_code =HTTPStatus.UNAUTHORIZED
    error_code="Invalid initialization key"
class AdminAlreadyExistsError(BaseAPIException):
    status_code=HTTPStatus.CONFLICT 
    error_code="Admin already exists"

class InvalidPasswordError(BaseAPIException):
    status_code=HTTPStatus.BAD_REQUEST
    error_code="Invalid password"

class UserNotFoundError(BaseAPIException):
    status_code=HTTPStatus.NOT_FOUND
    error_code="User not found"



