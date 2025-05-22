from http import HTTPStatus

from app.shared.domain.exceptions.common_errors import BaseAPIException


class DatabaseError(BaseAPIException):
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR
    error_code="Database error"



