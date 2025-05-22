from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

@dataclass
class OrderUpdatedEvent:
    """
    Event representing an order that has been updated.
    Contains the order ID and relevant information about the update.
    """
    order_id: str
    old_status: str
    new_status: str
    updated_by: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderUpdatedEvent':
        """
        Create an OrderUpdatedEvent from a dictionary.
        
        Args:
            data: Dictionary containing the event data
            
        Returns:
            OrderUpdatedEvent instance
        """
        return cls(
            order_id=data.get('order_id'),
            old_status=data.get('old_status'),
            new_status=data.get('new_status'),
            updated_by=data.get('updated_by'),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            metadata=data.get('metadata')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            'type': 'order.updated',
            'order_id': self.order_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'updated_by': self.updated_by,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }

