import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.category_service.application.dtos.category_dto import CategoryResponseDto, CategoryListDto
from app.services.category_service.application.queries.get_category_by_id import GetCategoryByIdQuery
from app.services.category_service.application.queries.get_categories_by_filter import GetCategoriesByFilterQuery
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork

# Configure logger
logger = logging.getLogger(__name__)

class CategoryQueryService:
    """
    Service for querying categories.
    """
    
    def __init__(self, session: Session, uow: UnitOfWork):
        self._session = session
        self._uow = uow
    
    def get_by_id(self, query: GetCategoryByIdQuery) -> Optional[CategoryResponseDto]:
        """
        Get a category by ID.
        
        Args:
            query: Query containing the ID of the category to retrieve
            
        Returns:
            Category response DTO if found, None otherwise
        """
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
    
    def list(self, query: GetCategoriesByFilterQuery) -> CategoryListDto:
        """
        List categories with optional filtering and pagination.
        
        Args:
            query: Query containing filter and pagination parameters
            
        Returns:
            Category list DTO with pagination information
        """
        from app.services.category_service.application.use_cases.list_categories import ListCategoriesUseCase
        
        list_use_case = ListCategoriesUseCase(self._uow)
        return list_use_case.execute(query) 