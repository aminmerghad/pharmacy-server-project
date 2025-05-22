from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.services.product_service.domain.entities.product_entity import ProductEntity


class ProductRepository(ABC):
    """
    Repository interface for product persistence operations.
    """
    
    @abstractmethod
    def add(self, product: ProductEntity) -> ProductEntity:
        """
        Add a new product to the repository.
        
        Args:
            product: The product entity to add
            
        Returns:
            The added product entity with generated ID
        """
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Optional[ProductEntity]:
        """
        Get a product by its ID.
        
        Args:
            product_id: The ID of the product to retrieve
            
        Returns:
            The product entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update(self, product: ProductEntity) -> ProductEntity:
        """
        Update an existing product.
        
        Args:
            product: The product entity with updated values
            
        Returns:
            The updated product entity
        """
        pass
    
    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """
        Delete a product by its ID.
        
        Args:
            product_id: The ID of the product to delete
            
        Returns:
            True if the product was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None, 
             page: int = 1, 
             page_size: int = 20) -> List[ProductEntity]:
        """
        List products with optional filtering and pagination.
        
        Args:
            filters: Optional dictionary of filter criteria
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of product entities matching the criteria
        """
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count products matching the specified filters.
        
        Args:
            filters: Optional dictionary of filter criteria
            
        Returns:
            Count of products matching the criteria
        """
        pass 