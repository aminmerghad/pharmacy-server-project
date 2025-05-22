from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class Repository(ABC):
    """
    Abstract base class for all repositories.
    
    This interface defines the common methods that all repositories must implement,
    providing a consistent interface for data access across the application.
    """
    
    @abstractmethod
    def add(self, entity):
        """Add a new entity to the repository"""
        pass
    
    @abstractmethod
    def get_by_id(self, id):
        """Retrieve an entity by its ID"""
        pass
    
    @abstractmethod
    def _to_model(self, entity):
        """Convert a domain entity to a database model"""
        pass
    
    @abstractmethod
    def _to_entity(self, model):
        """Convert a database model to a domain entity"""
        pass


class SQLAlchemyRepository(Repository):
    """
    Base implementation of Repository using SQLAlchemy.
    
    This class provides common functionality for SQLAlchemy-based repositories,
    including session management and basic CRUD operations.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            session: An SQLAlchemy session for database operations
        """
        self._session = session 