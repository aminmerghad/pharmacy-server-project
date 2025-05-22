from dataclasses import dataclass, field
from http import HTTPStatus
from app.shared.domain.exceptions.common_errors import BaseAPIException


class OrderError(Exception):
    """Base exception for order service"""
    pass

@dataclass
class OrderNotFoundError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND
    error_code: str = "ORDER_NOT_FOUND"
    message: str = "Order not found"
    error: dict = field(default_factory=dict)

class OrderValidationError(OrderError):
    pass

@dataclass
class InvalidOrderStatusTransition(BaseAPIException):
    """Raised when attempting an invalid order status transition"""
    status_code: HTTPStatus = HTTPStatus.CONFLICT
    error_code: str = "Status_Transition_ERROR"
    message: str = "Status Transition ERROR"
    error: dict = field(default_factory=dict)

class InsufficientStockError(OrderError):
    """Raised when there is insufficient stock for an order"""
    pass

class ProductNotFoundError(OrderError):
    """Raised when a product is not found"""
    pass

class OrderCancellationError(OrderError):
    """Raised when there is an error cancelling an order"""
    pass

class DuplicateOrderError(OrderError):
    """Raised when attempting to create a duplicate order"""
    pass

class InvalidQuantityError(OrderError):
    """Raised when an invalid quantity is specified"""
    pass

class InvalidPriceError(OrderError):
    """Raised when an invalid price is specified"""
    pass

@dataclass
class OrderCreationError(BaseAPIException):
    status_code: HTTPStatus = HTTPStatus.CONFLICT
    error_code: str = "Order_Creation_Error"
    message: str = "Order creation error"
    errors: dict = field(default_factory=dict)