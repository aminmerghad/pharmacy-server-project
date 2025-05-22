

from http import HTTPStatus


from typing import Optional
from http import HTTPStatus
from dataclasses import dataclass, field

from app.shared.domain.exceptions.common_errors import BaseAPIException

@dataclass
class   InventoryNotFoundError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND
    error_code: str = "PRODUCT_NOT_FOUND"
    message: str = "Product not found"
    error: dict = field(default_factory=dict)

@dataclass
class ProductNotFoundError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND
    error_code: str = "PRODUCT_NOT_FOUND"
    message: str = "Product not found"
    error: dict = field(default_factory=dict)

@dataclass
class DeleteProductError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.CONFLICT
    error_code: str = "DELETE_PRODUCT_ERROR"
    message: str = "Delete product error"
    error: dict = field(default_factory=dict)

