from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.services.inventory_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.inventory_service.infrastructure.query_services.inventory_query_service import InventoryQueryService
from app.services.product_service.application.queries.get_inventory_by_id import GetInventoryByIdQuery
from app.services.product_service.application.queries.get_product_by_id import GetProductByIdQuery


class GetInventoryPort(ABC):
    """Primary/Incoming port for stock checking"""
    @abstractmethod
    def get_inventory_by_id(self, request:Dict[str,Any]) -> Dict[str,Any]:
        pass

class GetInventoryAdapter(GetInventoryPort):
    """Incoming adapter for Inventory Service"""
    def __init__(self, inventory_query_service: InventoryQueryService):
        self._inventory_query_service = inventory_query_service

    def get_inventory_by_id(self, request: Dict[str,Any]) -> Dict[str,Any]:           
        # Execute use case
        result = self._inventory_query_service.get_inventory_by_id(
            GetInventoryByIdQuery(
                product_id=request.get('product_id')
            )
        )
        return result.model_dump()
        