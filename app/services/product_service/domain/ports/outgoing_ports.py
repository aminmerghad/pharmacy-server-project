from abc import ABC, abstractmethod
from typing import Any, Dict
from app.services.product_service.domain.requests.get_inventory_by_id_request import GetInventoryByIdRequest


class ProductServicePort(ABC):
    @abstractmethod
    def get_inventory_by_id(self, request: GetInventoryByIdRequest) -> Dict[str,Any]:
        pass