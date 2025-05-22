from datetime import datetime
import logging
from uuid import UUID

from pydantic import BaseModel

from app.services.category_service.application.commands.update_category_command import UpdateCategoryCommand
from app.services.category_service.domain.entities.category_entity import CategoryEntity
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.category_service.application.dtos.category_dto import CategoryFieldsDto
from app.shared.domain.exceptions.common_errors import ResourceNotFoundError

# Configure logger
logger = logging.getLogger(__name__)

class UpdateCategoryResponseDTO(BaseModel):
    id: UUID
    category_fields: CategoryFieldsDto

class UpdateCategoryUseCase:
    """
    Use case for updating an existing category.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, command: UpdateCategoryCommand) -> UpdateCategoryResponseDTO:
        logger.info(f"Updating category with ID: {command.id}")
        
        # Get existing category
        existing_category = self._uow.category_repository.get_by_id(command.id)
        if not existing_category:
            logger.warning(f"Category not found with ID: {command.id}")
            raise ResourceNotFoundError(f"Category not found with ID: {command.id}")
        
        # Update the category
        updated_category = self._update_category(existing_category, command)
        
        # Commit the transaction
        self._uow.commit()
        
        # Prepare response
        response = self._create_update_response_dto(updated_category)
        
        logger.info(f"Category updated successfully with ID: {updated_category.id}")
        
        return response
    
    def _update_category(self, existing_category: CategoryEntity, command: UpdateCategoryCommand) -> CategoryEntity:
        """Update an existing category entity."""
        # Create updated fields
        update_data = command.category_fields.model_dump(exclude_unset=True)
        
        # Update only provided fields, preserving existing values for others
        for key, value in update_data.items():
            if value is not None:  # Only update non-None values
                setattr(existing_category, key, value)
        
        # Set updated timestamp
        existing_category.updated_at = datetime.now()
        
        # Update in repository
        updated_category = self._uow.category_repository.update(existing_category)
        
        return updated_category
    
    def _create_update_response_dto(self, category: CategoryEntity) -> UpdateCategoryResponseDTO:
        """Create a response DTO with updated category information."""
        return UpdateCategoryResponseDTO(
            id=category.id,
            category_fields=CategoryFieldsDto(**category.model_dump())
        ) 