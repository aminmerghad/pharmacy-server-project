from abc import ABC, abstractmethod
from typing import Any

from app.services.category_service.domain.interfaces.category_repository import CategoryRepository

class UnitOfWork(ABC):
    @property
    @abstractmethod
    def category_repository(self) -> CategoryRepository:
        pass
    
    @abstractmethod
    def commit(self) -> None:
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        pass
    
    @abstractmethod
    def publish(self, event: Any) -> None:
        pass 