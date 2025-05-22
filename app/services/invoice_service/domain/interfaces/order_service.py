from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class OrderService(ABC):
    """Interface for interacting with the Order Service."""
    
    @abstractmethod
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details from the Order Service.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            A dictionary containing order details
            
        Raises:
            OrderServiceException: If the order cannot be retrieved
        """
        pass
    
    @abstractmethod
    def get_orders_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            A list of dictionaries containing order details
        """
        pass
    
    @abstractmethod
    def update_order_status(self, order_id: str, status: str) -> bool:
        """
        Update the status of an order.
        
        Args:
            order_id: The ID of the order to update
            status: The new status
            
        Returns:
            True if the update is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_order(self, order_id: str) -> bool:
        """
        Validate that an order exists and is in a valid state for invoicing.
        
        Args:
            order_id: The ID of the order to validate
            
        Returns:
            True if the order is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Get the items in an order.
        
        Args:
            order_id: The ID of the order
            
        Returns:
            A list of dictionaries containing item details
        """
        pass 