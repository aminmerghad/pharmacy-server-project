from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID
from dataclasses import dataclass, field
from app.services.order_service.domain.enums.stock_status import OrderStockStatus
from app.shared.contracts.inventory.stock_check import (
    StockCheckRequestContract,
    StockCheckResponseContract
)

# @dataclass
# class StockCheckItem:
#     product_id: UUID
#     quantity: int
#     available_quantity: int
#     status: OrderStockStatus

# @dataclass
# class InventoryCheckRequest:
#     customer_id: Optional[str] = None
#     items: List[StockCheckItem] = field(default_factory=list)

# @dataclass
# class StockCheck:
#     is_available: bool
#     unavailable_items: List[StockCheckItem] = field(default_factory=list)

class InventoryServicePort(ABC):
    @abstractmethod
    def stock_check(self, request: StockCheckRequestContract) -> StockCheckResponseContract:
        pass
   


