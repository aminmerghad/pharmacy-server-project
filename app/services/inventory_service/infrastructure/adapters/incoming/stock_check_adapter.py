from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from app.services.inventory_service.domain.ports.incoming_ports import StockCheckPort
from app.shared.contracts.inventory.enums import StockStatusContract
from app.shared.contracts.inventory.stock_check import (
    StockCheckRequestContract,
    StockCheckResponseContract,
    StockCheckItemContract
)
from app.services.inventory_service.domain.enums.stock_status import StockStatus



class StockCheckAdapter(StockCheckPort):
    """Incoming adapter for Inventory Service"""
    def __init__(self, stock_check_use_case):
        self._use_case = stock_check_use_case

    def stock_check(self, request: StockCheckRequestContract) -> StockCheckResponseContract:      
        
        # Execute use case
        result = self._use_case.execute(request)
        return result