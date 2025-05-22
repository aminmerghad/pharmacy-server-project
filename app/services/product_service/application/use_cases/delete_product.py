from datetime import datetime, timezone
from uuid import UUID
import logging

from pydantic import BaseModel

from app.services.product_service.application.commands.delete_product_command import DeleteProductCommand
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.shared.application.events.event_bus import EventBus

class DeleteProductResponseDTO(BaseModel):
    id: UUID
    message: str
    success: bool

# Configure logger
logger = logging.getLogger(__name__)

class DeleteProductUseCase:
    """
    Use case for deleting a product.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, command: DeleteProductCommand) -> DeleteProductResponseDTO:
        logger.info(f"Deleting product with ID: {command.id}")       
        
        # Get product to verify it exists before deletion
        product = self._get_product(command.id)
        
        # Delete product
        success = self._delete_product(command.id)
                
        # Commit the transaction
        self._uow.commit()
        
        # Create response
        response = self._create_response_dto(product.id, success)
        
        logger.info(f"Product deleted successfully: {product.id}")
        return response.model_dump()
    
    def _get_product(self, product_id: UUID):
        
        product = self._uow.product_repository.get_by_id(product_id)
        
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
            
        return product
    
    def _delete_product(self, product_id: UUID) -> bool:
        success = self._uow.product_repository.delete(product_id)
        
        if not success:
            raise ValueError(f"Failed to delete product with ID {product_id}")
            
        return success
    
    def _create_response_dto(self, product_id: UUID, success: bool) -> DeleteProductResponseDTO:
        return DeleteProductResponseDTO(
            id=product_id,
            message=f"Product with ID {product_id} deleted successfully" if success else f"Failed to delete product with ID {product_id}",
            success=success
        )