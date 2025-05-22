import logging
from typing import Optional
from uuid import UUID

from app.services.category_service.application.dtos.category_dto import CategoryResponseDto
from app.services.category_service.application.queries.get_category_by_id import GetCategoryByIdQuery
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork

# Configure logger
logger = logging.getLogger(__name__)

class GetCategoryUseCase:
    """
    Use case for retrieving a category by ID.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, query: GetCategoryByIdQuery) -> Optional[CategoryResponseDto]:
        logger.info(f"Getting category with ID: {query.id}")
        
        # Get category from repository
        category = self._uow.category_repository.get_by_id(query.id)
        
        if not category:
            logger.info(f"Category not found with ID: {query.id}")
            return None
        
        # Create response DTO
        response = CategoryResponseDto(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            image_url=category.image_url,
            is_active=category.is_active
        )
        
        logger.info(f"Category found with ID: {query.id}")
        
        return response 