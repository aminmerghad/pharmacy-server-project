from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel
from app.services.product_service.domain.enums.product_status import ProductStatus
from app.shared.domain.exceptions.common_errors import ValidationError
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto

@dataclass
class UpdateProductCommand:
    id: UUID
    product_fields: ProductFieldsDto
    inventory_fields: Optional[InventoryFieldsDto] = None

    def __init__(self, **kwargs):
        # Extract the ID - either 'id' or 'product_id' could be provided
        self.id = kwargs.get('id') or kwargs.get('product_id')
        if not self.id:
            raise ValidationError("Product ID is required for update")
        
        # Get nested data structures
        product_data = kwargs.get('product_fields', {})
        inventory_data = kwargs.get('inventory_fields', {})
        
        # Initialize nested data objects
        self.product_fields = ProductFieldsDto(**product_data)
        
        # Inventory fields are optional for updates
        if inventory_data:
            self.inventory_fields = InventoryFieldsDto(**inventory_data)
            self.inventory_fields.validate()
        else:
            self.inventory_fields = None
            
        # Validate product fields
        self.product_fields.validate()


