from math import ceil
from typing import List, Dict, Any, Optional
import logging

from pydantic import BaseModel

from app.services.product_service.application.queries.get_products_by_filter import GetProductsByFilterQuery
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto

class ProductItemDTO(BaseModel):
    id: str
    product_fields: ProductFieldsDto
    inventory_fields: Optional[InventoryFieldsDto] = None

class ProductListDTO(BaseModel):
    items: List[ProductItemDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

# Configure logger
logger = logging.getLogger(__name__)

class ListProductsUseCase:
    """
    Use case for listing products with filtering and pagination.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, query: GetProductsByFilterQuery) -> Dict[str, Any]:
        logger.info(f"Listing products with filters: {query.filters}")
        
        # Get products from repository with pagination
        products, total_count = self._get_products(query)
        
        # Calculate pagination info
        total_pages = ceil(total_count / query.page_size) if total_count > 0 else 1
        
        # Create response DTO
        response = self._create_product_list_dto(products, total_count, query.page, query.page_size, total_pages)
        
        logger.info(f"Retrieved {total_count} products (page {query.page} of {total_pages})")
        return response.model_dump()
    
    def _get_products(self, query: GetProductsByFilterQuery):
        products = self._uow.product_repository.list(
            filters=query.filters,
            page=query.page,
            page_size=query.page_size
        )
        
        # Get total count for pagination
        total_count = self._uow.product_repository.count(filters=query.filters)
        
        return products, total_count
    
    def _create_product_list_dto(self, products, total_count, page, page_size, total_pages) -> ProductListDTO:
        product_dtos = []
        
        for product in products:
            # Get inventory data for this product if available
            inventory_data = self._get_inventory_data(product.id)
            
            product_dto = ProductItemDTO(
                id=str(product.id),
                product_fields=ProductFieldsDto(**product.model_dump()),
                inventory_fields=InventoryFieldsDto(**inventory_data) if inventory_data else None
            )
            
            product_dtos.append(product_dto)
        
        return ProductListDTO(
            items=product_dtos,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def _get_inventory_data(self, product_id) -> Optional[Dict[str, Any]]:
        # This would typically query the inventory service or a local cache
        # For now, we'll just return a simplified approach
        try:
            inventory = self._uow.inventory_repository.get_by_product_id(product_id) if hasattr(self._uow, 'inventory_repository') else None
            
            if inventory:
                return inventory.model_dump()
            return None
        except Exception as e:
            logger.warning(f"Error retrieving inventory data for product {product_id}: {str(e)}")
            return None