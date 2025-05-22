import logging
import math
from typing import List, Dict, Any

from app.services.category_service.application.dtos.category_dto import CategoryResponseDto, CategoryListDto
from app.services.category_service.application.queries.get_categories_by_filter import GetCategoriesByFilterQuery
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.category_service.domain.entities.category_entity import CategoryEntity

# Configure logger
logger = logging.getLogger(__name__)

class ListCategoriesUseCase:
    """
    Use case for listing categories with filtering and pagination.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, query: GetCategoriesByFilterQuery) -> CategoryListDto:
        logger.info(f"Listing categories with filters: {query.model_dump()}")
        
        # Get categories from repository with filtering
        all_categories = self._uow.category_repository.get_all()
        
        # Apply filters
        filtered_categories = self._apply_filters(all_categories, query)
        
        # Apply sorting
        sorted_categories = self._apply_sorting(filtered_categories, query.sort_by, query.sort_direction)
        
        # Apply pagination
        paginated_result = self._apply_pagination(sorted_categories, query.page, query.items_per_page)
        
        # Create response DTO
        response = CategoryListDto(
            items=[self._create_category_response_dto(category) for category in paginated_result['items']],
            total_items=paginated_result['total_items'],
            page=query.page,
            page_size=query.items_per_page,
            total_pages=paginated_result['total_pages']
        )
        
        logger.info(f"Found {response.total_items} categories (page {query.page} of {response.total_pages})")
        
        return response
    
    def _apply_filters(self, categories: List[CategoryEntity], query: GetCategoriesByFilterQuery) -> List[CategoryEntity]:
        """Apply filters to the list of categories."""
        filtered = categories
        
        # Filter by name
        if query.name:
            filtered = [c for c in filtered if query.name.lower() in c.name.lower()]
        
        # Filter by parent_id
        if query.parent_id:
            filtered = [c for c in filtered if c.parent_id == query.parent_id]
        
        # Filter by active status
        if query.is_active is not None:
            filtered = [c for c in filtered if c.is_active == query.is_active]
        
        return filtered
    
    def _apply_sorting(self, categories: List[CategoryEntity], sort_by: str, sort_direction: str) -> List[CategoryEntity]:
        """Apply sorting to the list of categories."""
        reverse = sort_direction.lower() == 'desc'
        
        if sort_by == 'name':
            return sorted(categories, key=lambda c: c.name, reverse=reverse)
        
        # Default to sorting by name
        return sorted(categories, key=lambda c: c.name, reverse=reverse)
    
    def _apply_pagination(self, categories: List[CategoryEntity], page: int, page_size: int) -> Dict[str, Any]:
        """Apply pagination to the list of categories."""
        total_items = len(categories)
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        
        # Adjust page if out of bounds
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        # Calculate slice indices
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page items
        items = categories[start_idx:end_idx]
        
        return {
            'items': items,
            'total_items': total_items,
            'total_pages': total_pages
        }
    
    def _create_category_response_dto(self, category: CategoryEntity) -> CategoryResponseDto:
        """Create a response DTO from a category entity."""
        return CategoryResponseDto(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            image_url=category.image_url,
            is_active=category.is_active
        ) 