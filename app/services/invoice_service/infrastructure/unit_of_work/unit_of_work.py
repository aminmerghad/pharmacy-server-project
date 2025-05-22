from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.infrastructure.persistence.invoice_repository_impl import SQLAlchemyInvoiceRepository

class UnitOfWork(ABC):
    """
    Abstract Unit of Work interface.
    Defines the contract for transaction management.
    """
    
    @abstractmethod
    def __enter__(self):
        """Begin the unit of work."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the unit of work."""
        pass
    
    @abstractmethod
    def commit(self):
        """Commit the changes."""
        pass
    
    @abstractmethod
    def rollback(self):
        """Rollback the changes."""
        pass
    
    @property
    @abstractmethod
    def invoices(self) -> InvoiceRepository:
        """Get access to the invoice repository."""
        pass


class SQLAlchemyUnitOfWork(UnitOfWork):
    """
    SQLAlchemy implementation of the Unit of Work pattern.
    Manages transaction boundaries and provides access to repositories.
    """
    
    def __init__(self, session):
        """
        Initialize with a session factory function.
        
        Args:
            session_factory: A callable that creates a new SQLAlchemy session
        """
        self.session = session
    
    def __enter__(self):
        """Begin the unit of work by creating a new session."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the unit of work by closing the session."""
        if exc_type is not None:
            self.rollback()
        
        self.session.close()
    
    def commit(self):
        """Commit the transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback the transaction."""
        self.session.rollback()
    
    @property
    def invoices(self) -> InvoiceRepository:
        """Get access to the invoice repository."""
        return SQLAlchemyInvoiceRepository(self.session) 