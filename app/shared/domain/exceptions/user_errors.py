from http import HTTPStatus
from app.shared.domain.exceptions.common_errors import BaseAPIException


class UserAlreadyExistsError(BaseAPIException):
    status_code=HTTPStatus.CONFLICT
    error_code="Integrity error"