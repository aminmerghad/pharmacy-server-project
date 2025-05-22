from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto
from app.shared.domain.exceptions.common_errors import ValidationError




@dataclass
class CreateProductCommand:
    product_fields: ProductFieldsDto
    inventory_fields: InventoryFieldsDto
    product_id: Optional[UUID] = None

    def __init__(self, **kwargs):
        # Fix typos in the keys and use proper initialization
        product_data = kwargs.get('product_fields', {})
        inventory_data = kwargs.get('inventory_fields', {})

        if kwargs.get('product_id'):
            self.product_id= kwargs.get('product_id')
        
        # Use proper initialization of nested dataclasses
        self.product_fields = ProductFieldsDto(**product_data)               
        self.inventory_fields = InventoryFieldsDto(**inventory_data)       
        self.product_fields.validate()
        self.inventory_fields.validate()



