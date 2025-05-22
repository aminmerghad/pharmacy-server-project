from abc import ABC, abstractmethod
from app.services.product_service.domain.interfaces.repository import ProductRepository
from app.services.product_service.domain.interfaces.product_adapter_service import ProductAdapterService
from app.shared.application.events.event_bus import Event


class UnitOfWork(ABC):
    """
    Unit of Work interface for managing transactions and repository access.
    """
    
    @property
    @abstractmethod
    def product_repository(self) -> ProductRepository:
        """
        Get the product repository.
        
        Returns:
            The product repository instance
        """
        pass
    
    @property
    @abstractmethod
    def product_adapter_service(self) -> ProductAdapterService:
        """
        Get the product adapter service.
        
        Returns:
            The product adapter service instance
        """
        pass
    
    @abstractmethod
    def begin(self) -> None:
        """
        Begin a new transaction.
        """
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback the current transaction.
        """
        pass
    
    @abstractmethod
    def __enter__(self):
        """
        Enter the context manager, beginning a new transaction.
        
        Returns:
            The unit of work instance
        """
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, committing or rolling back the transaction.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        pass 
    
    @abstractmethod
    def publish(self,event:Event) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event: The event to publish
        """
        pass