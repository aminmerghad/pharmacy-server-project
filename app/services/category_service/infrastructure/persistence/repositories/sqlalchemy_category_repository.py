import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.services.category_service.domain.entities.category_entity import CategoryEntity
from app.services.category_service.domain.interfaces.category_repository import CategoryRepository
from app.services.category_service.infrastructure.persistence.models.category import Category

# Configure logger
logger = logging.getLogger(__name__)

class SQLAlchemyCategoryRepository(CategoryRepository):
    """
    SQLAlchemy implementation of the CategoryRepository interface.
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def add(self, category: CategoryEntity) -> CategoryEntity:
        """
        Add a new category to the repository.
        
        Args:
            category: The category entity to add
            
        Returns:
            The added category entity with ID
        """
        # Create a new ID if not provided
        if not category.id:
            category.id = uuid4()
        
        # Set timestamps
        now = datetime.now()
        category.created_at = now
        category.updated_at = now
        
        # Create ORM model
        db_category = Category(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            image_url=category.image_url,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
        # Add to session
        self._session.add(db_category)
        self._session.flush()
        
        # Update entity with DB values
        return self._map_to_entity(db_category)
    
    def update(self, category: CategoryEntity) -> CategoryEntity:
        """
        Update an existing category in the repository.
        
        Args:
            category: The category entity with updated values
            
        Returns:
            The updated category entity
        """
        # Get existing category
        db_category = self._session.query(Category).filter(Category.id == category.id).first()
        
        if not db_category:
            logger.warning(f"Category not found for update: {category.id}")
            raise ValueError(f"Category not found with ID: {category.id}")
        
        # Update fields
        db_category.name = category.name
        db_category.description = category.description
        db_category.parent_id = category.parent_id
        db_category.image_url = category.image_url
        db_category.is_active = category.is_active
        db_category.updated_at = datetime.now()
        
        # Flush changes
        self._session.flush()
        
        # Return updated entity
        return self._map_to_entity(db_category)
    
    def delete(self, category_id: UUID) -> None:
        """
        Delete a category from the repository.
        
        Args:
            category_id: The ID of the category to delete
        """
        # Soft delete by setting is_active to False
        db_category = self._session.query(Category).filter(Category.id == category_id).first()
        
        if not db_category:
            logger.warning(f"Category not found for deletion: {category_id}")
            raise ValueError(f"Category not found with ID: {category_id}")
        
        # Perform soft delete
        db_category.is_active = False
        db_category.updated_at = datetime.now()
        
        # Flush changes
        self._session.flush()
    
    def get_by_id(self, category_id: UUID) -> Optional[CategoryEntity]:
        """
        Get a category by ID.
        
        Args:
            category_id: The ID of the category to retrieve
            
        Returns:
            Category entity if found, None otherwise
        """
        db_category = self._session.query(Category).filter(Category.id == category_id).first()
        
        if not db_category:
            return None
        
        return self._map_to_entity(db_category)
    
    def get_all(self) -> List[CategoryEntity]:
        """
        Get all categories.
        
        Returns:
            List of all category entities
        """
        db_categories = self._session.query(Category).all()
        
        return [self._map_to_entity(db_category) for db_category in db_categories]
    
    def _map_to_entity(self, db_category: Category) -> CategoryEntity:
        """
        Map a database model to a domain entity.
        
        Args:
            db_category: The database category model
            
        Returns:
            Category domain entity
        """
        return CategoryEntity(
            id=db_category.id,
            name=db_category.name,
            description=db_category.description,
            parent_id=db_category.parent_id,
            image_url=db_category.image_url,
            is_active=db_category.is_active,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at
        ) 