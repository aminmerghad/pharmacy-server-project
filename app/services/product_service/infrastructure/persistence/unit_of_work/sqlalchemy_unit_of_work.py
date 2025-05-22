from typing import Any
from sqlalchemy.orm import Session

from app.services.product_service.infrastructure.adapters.outgoing.product_adapter import ProductServiceAdapter
from app.services.product_service.infrastructure.persistence.repositories.product_repository import ProductRepository
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.product_service.domain.interfaces.product_adapter_service import ProductAdapterService
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus


class SQLAlchemyUnitOfWork(UnitOfWork):
    """
    SQLAlchemy implementation of the Unit of Work pattern.
    """
    
    def __init__(self, session: Session, event_bus: EventBus, acl: UnifiedACL):
        """
        Initialize the unit of work with a database session.
        
        Args:
            session: SQLAlchemy database session
            event_bus: Event bus for publishing events
            acl: Unified ACL for access control
            inventory_service_url: URL for the inventory service
        """
        self._session = session
        self._event_bus = event_bus
        self._acl = acl
        self._product_repository = None
        self._product_adapter_service = None
    
    @property
    def product_repository(self) -> ProductRepository:
        """
        Get the product repository.
        
        Returns:
            The product repository instance
        """
        if not self._product_repository:
            self._product_repository = ProductRepository(self._session)
        
        return self._product_repository
    
    @property
    def product_adapter_service(self) -> ProductAdapterService:
        """
        Get the product adapter service.
        
        Returns:
            The product adapter service instance
        """
        if not self._product_adapter_service:
            self._product_adapter_service = ProductServiceAdapter(self._acl)
        
        return self._product_adapter_service
    
    def begin(self) -> None:
        """
        Begin a new transaction.
        """
        # Session is already created, nothing to do here
        pass
    
    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        self._session.commit()
    
    def rollback(self) -> None:
        """
        Rollback the current transaction.
        """
        self._session.rollback()
    
    def __enter__(self):
        """
        Enter the context manager, beginning a new transaction.
        
        Returns:
            The unit of work instance
        """
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, committing or rolling back the transaction.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if exc_type:
            self.rollback()
        else:
            self.commit()
    
    def publish(self, event: Any) -> None:
        self._event_bus.publish(event)