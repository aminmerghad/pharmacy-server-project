from abc import ABC, abstractmethod

class UnitOfWork(ABC):
    """Interface for the Unit of Work pattern."""
    
    @abstractmethod
    def __enter__(self):
        """Enter the unit of work context."""
        pass
        
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the unit of work context."""
        pass
        
    @abstractmethod
    def commit(self):
        """Commit the unit of work."""
        pass
        
    @abstractmethod
    def rollback(self):
        """Rollback the unit of work."""
        pass 