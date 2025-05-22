from abc import ABC, abstractmethod
from app.shared.contracts.inventory.stock_check import (
    StockCheckRequestContract,
    StockCheckResponseContract
)

class StockCheckPort(ABC):
    """Primary/Incoming port for stock checking"""
    @abstractmethod
    def stock_check(self, request: StockCheckRequestContract) -> StockCheckResponseContract:
        pass 