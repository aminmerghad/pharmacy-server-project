from abc import ABC, abstractmethod
from typing import Dict, Any
from uuid import UUID

from app.services.product_service.application.dtos.product_dto import InventoryFieldsDto
from app.services.product_service.domain.requests.get_inventory_by_id_request import GetInventoryByIdRequest


class ProductAdapterService(ABC):
    """
    Interface for adapter services that connect the product service to other services.
    """
    
    @abstractmethod
    def get_inventory_by_id(self, request: GetInventoryByIdRequest) -> InventoryFieldsDto:
        """
        Get inventory information for a product.
        
        Args:
            request: Request containing the product ID
            
        Returns:
            Dictionary with inventory information
        """
        pass 