from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel
from app.shared.contracts.inventory.enums import StockStatusContract

# Error types for stock check
class StockCheckErrorType(str, Enum):
    INSUFFICIENT_STOCK = "insufficient_stock"
    PRODUCT_NOT_FOUND = "product_not_found"
    INVENTORY_NOT_FOUND = "inventory_not_found"
    PRODUCT_INACTIVE = "product_inactive"
    PRODUCT_EXPIRED = "product_expired"
    VALIDATION_ERROR = "validation_error"
    GENERIC_ERROR = "generic_error"
# Status types for stock items


@dataclass
class StockCheckErrorDetail:
    error_type: StockCheckErrorType
    message: str
    product_id: Optional[UUID] = None    
    details: Dict[str, Any] = None
    
class StockCheckItemContract(BaseModel):
    product_id: UUID =None
    quantity: int =None
    available_quantity: Optional[int] = None
    status: Optional[StockStatusContract] = None

class StockItemValidationContract(BaseModel):
    is_available: bool
    remaining_stock: int
    warnings: List[str]
    status: List[StockStatusContract]
    days_until_expiry: Optional[int] = None

class StockItemResultContract(BaseModel):
    product_id: UUID    
    product_name: str
    requested_quantity: int
    available_quantity: int
    minimum_stock_level:int
    maximum_stock_level:int
    unit_price: Optional[float] = None
    expiry_date: Optional[datetime] = None
    stock_validation_result:StockItemValidationContract
    # message: str

class StockCheckRequestContract(BaseModel):
    consumer_id: Optional[UUID] = None
    items: List[StockCheckItemContract] = []


# class StockCheckResponseContract(BaseModel):
#     is_available: bool
#     unavailable_items: List[StockCheckItemContract] = field(default_factory=list)

class StockCheckSummaryContract(BaseModel):
    total_items: int
    available_items: int
    unavailable_items: int
    details: Dict[str, int] = None

class StockCheckResponseContract(BaseModel):
    """Contract for a stock check response"""
    success: bool
    message: str
    data: Optional[List[StockItemResultContract]] = None
    summary: Optional[StockCheckSummaryContract] = None
    errors: Optional[List[StockCheckErrorDetail]] = None

    def is_legit(self):
        return self.summary.available_items == self.summary.total_items
    
    