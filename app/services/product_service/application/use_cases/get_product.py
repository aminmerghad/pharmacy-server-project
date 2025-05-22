from uuid import UUID
import logging
from typing import Optional, Dict, Any

from pydantic import BaseModel

from app.services.product_service.application.queries.get_product_by_id import GetProductByIdQuery
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto
from app.services.product_service.domain.requests.get_inventory_by_id_request import GetInventoryByIdRequest

# Configure logger
logger = logging.getLogger(__name__)

class GetProductResponseDTO(BaseModel):
    id: UUID
    product_fields: ProductFieldsDto
    inventory_fields: Optional[InventoryFieldsDto] = None

class GetProductUseCase:
    """
    Use case for retrieving a product by its ID.
    """
    
    def __init__(self, uow: UnitOfWork):        
        self._uow = uow
    
    def execute(self, query: GetProductByIdQuery) -> ProductFieldsDto:
        
        logger.info(f"Getting product with ID: {query.id}")
        
        try:
            # Get the product from repository
            product = self._uow.product_repository.get_by_id(query.id)
            
            if not product:
                logger.info(f"Product with ID {query.id} not found")
                return None
            # Get inventory information if available
            # inventory_data = self._get_inventory_data(product.id)
            
            # # Create response DTO
            # response = GetProductResponseDTO(
            #     id=product.id,
            #     product_fields=ProductFieldsDto(**product.model_dump()),
            #     inventory_fields=inventory_data
            # )
            
            logger.info(f"Retrieved product: {product.name}")
            return ProductFieldsDto(**product.model_dump())
            
        except Exception as e:
            logger.error(f"Error retrieving product: {str(e)}", exc_info=True)
            raise
    
    # def _get_inventory_data(self, product_id: UUID) -> Optional[InventoryFieldsDto]:
    #     """Get inventory data for a product"""
    #     adapter_service = self._uow.product_adapter_service
    #     get_inventory_result = adapter_service.get_inventory_by_id(
    #         GetInventoryByIdRequest(product_id=product_id)
    #     )


    #     return get_inventory_result

