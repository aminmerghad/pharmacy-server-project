from datetime import datetime
from uuid import UUID
import logging
from typing import Dict, Any

from pydantic import BaseModel

from app.services.category_service.application.commands.create_category_command import CreateCategoryCommand
from app.services.category_service.domain.entities.category_entity import CategoryEntity
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.category_service.application.dtos.category_dto import CategoryFieldsDto

# Configure logger
logger = logging.getLogger(__name__)

class CreateCategoryResponseDTO(BaseModel):
    id: UUID
    category_fields: CategoryFieldsDto

class CreateCategoryUseCase:
    """
    Use case for creating a new category.
    """
    
    def __init__(self, uow: UnitOfWork):        
        self._uow = uow
    
    def execute(self, command: CreateCategoryCommand) -> CreateCategoryResponseDTO:        
        logger.info(f"Creating category with name: {command.category_fields.name}")
        
        # Create the category entity
        category_entity = self._create_category(command)
            
        # Commit the transaction
        self._uow.commit()
            
        # Prepare response
        response = self._create_category_response_dto(category_entity)
        
        logger.info(f"Category created successfully with ID: {category_entity.id}")
          
        return response
    
    def _create_category(self, command: CreateCategoryCommand) -> CategoryEntity:
        """Create and persist a new category entity."""
        category_entity = self._uow.category_repository.add(
            CategoryEntity(**command.category_fields.model_dump())
        )
        return category_entity
    
    def _create_category_response_dto(self, category_entity: CategoryEntity) -> CreateCategoryResponseDTO:
        """Create a response DTO with category information."""
        return CreateCategoryResponseDTO(
            id=category_entity.id,
            category_fields=CategoryFieldsDto(**category_entity.model_dump())
        ) 