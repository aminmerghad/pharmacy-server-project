from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.services.category_service.domain.entities.category_entity import CategoryEntity

class CategoryRepository(ABC):
    @abstractmethod
    def add(self, category: CategoryEntity) -> CategoryEntity:
        pass
    
    @abstractmethod
    def update(self, category: CategoryEntity) -> CategoryEntity:
        pass
    
    @abstractmethod
    def delete(self, category_id: UUID) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, category_id: UUID) -> Optional[CategoryEntity]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[CategoryEntity]:
        pass 