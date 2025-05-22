from abc import ABC, abstractmethod
from typing import Dict, Any, List

class EventBusAdapter(ABC):
    """
    Adapter interface for publishing events to an event bus.
    This provides a clean abstraction over the specific event bus implementation.
    """
    
    @abstractmethod
    def publish(self, event: Dict[str, Any]) -> bool:
        """
        Publish an event to the event bus.
        
        Args:
            event: Event to publish, as a dictionary
            
        Returns:
            True if the event was published successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def publish_batch(self, events: List[Dict[str, Any]]) -> Dict[int, bool]:
        """
        Publish multiple events to the event bus.
        
        Args:
            events: List of events to publish, as dictionaries
            
        Returns:
            Dictionary mapping indices to success status
        """
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the event bus.
        
        Returns:
            True if the connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the event bus.
        
        Returns:
            True if the disconnection was successful, False otherwise
        """
        pass 