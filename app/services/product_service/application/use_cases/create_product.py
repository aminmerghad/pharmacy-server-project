from datetime import datetime, timezone
from uuid import UUID
import logging
from typing import Dict, Any

from pydantic import BaseModel

from app.services.product_service.application.commands.create_product_command import CreateProductCommand
from app.services.product_service.domain.entities.product_entity import ProductEntity
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.shared.application.events.event_bus import EventBus
from app.services.inventory_service.application.events.inventory_create_requested_event import InventoryCreateRequestedEvent
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto

# Configure logger
logger = logging.getLogger(__name__)

class CreateProductResponseDTO(BaseModel):
    id: UUID

    product_fields: ProductFieldsDto
    inventory_fields: InventoryFieldsDto


class CreateProductUseCase:
    """
    Use case for creating a new product with associated inventory.
    
    This use case handles:
    1. Creating a product entity in the database
    2. Preparing inventory data
    3. Publishing an event to create inventory
    4. Returning a comprehensive response with both product and inventory data
    """
    
    def __init__(self, uow: UnitOfWork):        
        self._uow = uow
    
    def execute(self, command: CreateProductCommand) -> CreateProductResponseDTO:        
        logger.info(f"Creating product with name: {command.product_fields.name}")
        
        # Create the product entity
        product_entity = self._create_product(command)
            
        # Prepare inventory data
        inventory_data = self._create_inventory_dict(command, product_entity)
            
        # Publish event to create inventory
        self._publish_inventory_event(inventory_data)
            
        # Commit the transaction
        self._uow.commit()
            
        # Prepare response
        response = self._create_product_response_dto(product_entity, inventory_data)
        
        logger.info(f"Product created successfully with ID: {product_entity.id}")
          
        return response
            
        
    
    def _create_product(self, command: CreateProductCommand) -> ProductEntity:
        """Create and persist a new product entity."""
        product_entity = self._uow.product_repository.add(
            ProductEntity(**command.product_fields.model_dump())
        )
        return product_entity
    
    def _create_inventory_dict(self, command: CreateProductCommand, product_entity: ProductEntity) -> Dict[str, Any]:
        """Prepare inventory data with product reference."""
        inventory_data = command.inventory_fields.model_dump()
        inventory_data['product_id'] = product_entity.id
        return inventory_data
    
    def _publish_inventory_event(self, inventory_data: Dict[str, Any]) -> None:
        """Publish event to trigger inventory creation."""
        try:
            #i need to handle event handle error in event Bus
            self._uow.publish( 
                InventoryCreateRequestedEvent(**inventory_data)
            )
            logger.info(f"Published InventoryCreateRequestedEvent for product: {inventory_data['product_id']}")
        except Exception as event_error:           
            # Log but don't fail if event publishing fails
            logger.warning(f"Failed to publish inventory creation event: {str(event_error)}")
            raise
    
    def _create_product_response_dto(self, product_entity: ProductEntity, inventory_data: Dict[str, Any]) -> CreateProductResponseDTO:
        """Create a response DTO with product and inventory information."""
        return CreateProductResponseDTO(
            id=product_entity.id,
            product_fields=ProductFieldsDto(**product_entity.model_dump()),
            inventory_fields=InventoryFieldsDto(**inventory_data)
        )