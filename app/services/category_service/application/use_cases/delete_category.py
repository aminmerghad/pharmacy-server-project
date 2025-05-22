import logging
from uuid import UUID

from pydantic import BaseModel

from app.services.category_service.application.commands.delete_category_command import DeleteCategoryCommand
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork
from app.shared.domain.exceptions.common_errors import ResourceNotFoundError

# Configure logger
logger = logging.getLogger(__name__)

class DeleteCategoryResponseDTO(BaseModel):
    id: UUID
    success: bool

class DeleteCategoryUseCase:
    """
    Use case for deleting a category.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, command: DeleteCategoryCommand) -> DeleteCategoryResponseDTO:
        logger.info(f"Deleting category with ID: {command.id}")
        
        # Check if category exists
        existing_category = self._uow.category_repository.get_by_id(command.id)
        if not existing_category:
            logger.warning(f"Category not found with ID: {command.id}")
            raise ResourceNotFoundError(f"Category not found with ID: {command.id}")
        
        # Delete the category
        self._uow.category_repository.delete(command.id)
        
        # Commit the transaction
        self._uow.commit()
        
        # Prepare response
        response = DeleteCategoryResponseDTO(
            id=command.id,
            success=True
        )
        
        logger.info(f"Category deleted successfully with ID: {command.id}")
        
        return response 