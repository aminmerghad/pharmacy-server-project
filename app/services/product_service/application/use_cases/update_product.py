from datetime import datetime, timezone
from uuid import UUID
import logging

from pydantic import BaseModel

from app.services.product_service.application.commands.update_product_command import UpdateProductCommand
from app.services.product_service.domain.entities.product_entity import ProductEntity
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.shared.application.events.event_bus import EventBus
from app.services.inventory_service.application.events.inventory_update_requested_event import InventoryUpdateRequestedEvent
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto

class UpdateProductResponseDTO(BaseModel):
    id: UUID
    product_fields: ProductFieldsDto
    inventory_fields: InventoryFieldsDto

# Configure logger
logger = logging.getLogger(__name__)

class UpdateProductUseCase:
    """
    Use case for updating an existing product.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, command: UpdateProductCommand) -> UpdateProductResponseDTO:
        logger.info(f"Updating product with ID: {command.id}")       
        product_fields_entity = self._update_product(command)
        inventory_fields_dict = self._update_inventory_dict(command, product_fields_entity)   
        self._publish_inventory_event(inventory_fields_dict)
        self._uow.commit()
        response = self._create_product_response_dto(product_fields_entity, inventory_fields_dict)
        logger.info(f"Product updated successfully: {response.product_fields.id}")
        return response

    def _create_product_response_dto(self, product_fields_entity: ProductEntity, inventory_fields_dict: dict) -> UpdateProductResponseDTO:
        return UpdateProductResponseDTO(
            id=product_fields_entity.id,
            product_fields=ProductFieldsDto(**product_fields_entity.model_dump()),
            inventory_fields=InventoryFieldsDto(**inventory_fields_dict)
        )
        
    def _update_product(self, command: UpdateProductCommand) -> ProductEntity:
        # Get existing product
        product = self._uow.product_repository.get_by_id(command.id)
        
        if not product:
            raise ValueError(f"Product with ID {command.id} not found")
        
        # Update fields if provided
        update_data = command.product_fields.model_dump(exclude_unset=True)
        
        # Update the product with the new data
        for field, value in update_data.items():
            setattr(product, field, value)
        
        
        
        # Save updated product
        updated_product = self._uow.product_repository.update(product)
        return updated_product
        
    def _update_inventory_dict(self, command: UpdateProductCommand, product_fields_entity: ProductEntity) -> dict:
        if not command.inventory_fields:
            # If no inventory fields provided, return empty dict
            return {}
            
        inventory_fields_dict = command.inventory_fields.model_dump(exclude_unset=True)
        inventory_fields_dict['product_id'] = product_fields_entity.id
        return inventory_fields_dict
        
    def _publish_inventory_event(self, inventory_fields_dict: dict):
        # Only publish event if there are inventory fields to update
        if not inventory_fields_dict:
            logger.info(f"No inventory fields to update, skipping event publishing")
            return
            
        try:    
            self._uow.publish(
                InventoryUpdateRequestedEvent(
                    **inventory_fields_dict
                )
            )
            logger.info(f"Published InventoryUpdateRequestedEvent event for product: {inventory_fields_dict['product_id']}")
        except Exception as event_error:
            # Log but don't fail if event publishing fails
            logger.warning(f"Failed to publish product.updated event: {str(event_error)}")