"""Result types for service operations."""
from dataclasses import dataclass
from typing import List, Optional, Any, Dict, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Base result type."""
    success: bool
    message: str
    data: Optional[T] = None
    error_code: Optional[str] = None
    error_details: Optional[Dict] = None

@dataclass
class Success(Result[T]):
    """Success result type."""
    def __init__(self, data: T = None, message: str = "Operation successful"):
        super().__init__(
            success=True,
            message=message,
            data=data
        )

@dataclass
class Failure(Result[T]):
    """Failure result type."""
    def __init__(self, message: str, error_code: str = None, error_details: Dict = None):
        super().__init__(
            success=False,
            message=message,
            error_code=error_code,
            error_details=error_details
        )

@dataclass
class ServiceResult:
    """Base result class for service operations."""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    error_details: Optional[Dict] = None
    
    @classmethod
    def success_result(cls, data: Any = None, message: str = "Operation successful"):
        return cls(success=True, message=message, data=data)
        
    @classmethod
    def failure_result(cls, message: str, error_code: str = None, error_details: Dict = None):
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            error_details=error_details
        )

@dataclass
class InventoryResult:
    """Result of inventory operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def success(cls, data: Any) -> 'InventoryResult':
        """Create success result."""
        return cls(success=True, data=data)
    
    @classmethod
    def failure(cls, error: str) -> 'InventoryResult':
        """Create failure result."""
        return cls(success=False, error=error)

@dataclass
class AvailabilityResult(ServiceResult):
    """Result class for availability checks."""
    is_available: bool = False
    available_quantity: int = 0
    location_availability: List[Dict] = None
    alternative_locations: Optional[List[Dict]] = None
    reservation_id: Optional[str] = None
    valid_until: Optional[datetime] = None
    
    @classmethod
    def from_cache(cls, cached_data: dict):
        return cls(
            success=True,
            message="Retrieved from cache",
            data=cached_data,
            is_available=cached_data['is_available'],
            available_quantity=cached_data['available_quantity'],
            location_availability=cached_data['location_availability'],
            alternative_locations=cached_data.get('alternative_locations'),
            reservation_id=cached_data.get('reservation_id'),
            valid_until=datetime.fromisoformat(cached_data['valid_until']) if cached_data.get('valid_until') else None
        )

# @dataclass
# class StockStatusResult(ServiceResult):
#     """Result class for stock status queries"""
#     # current_quantity: int
#     reorder_level: int
#     reorder_quantity: int
#     last_received: Optional[datetime] = None
#     last_adjusted: Optional[datetime] = None
#     expiry_date: Optional[datetime] = None
#     quality_status: Optional[str] = None
#     location_details: Optional[Dict] = None 