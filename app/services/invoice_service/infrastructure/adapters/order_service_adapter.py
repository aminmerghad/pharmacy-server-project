from typing import Dict, Any, List, Optional
import requests
import logging

from app.services.invoice_service.domain.interfaces.order_service import OrderService

logger = logging.getLogger(__name__)

class OrderServiceAdapter(OrderService):
    """Adapter for interacting with the Order Service."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the adapter with configuration.
        
        Args:
            base_url: The base URL of the Order Service API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for API requests."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details from the Order Service.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            A dictionary containing order details
            
        Raises:
            Exception: If the order cannot be retrieved
        """
        try:
            response = requests.get(
                f"{self.base_url}/order/orders/{order_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"Failed to get order {order_id}: {str(e)}")
            if e.response.status_code == 404:
                raise ValueError(f"Order {order_id} not found")
            raise Exception(f"Error retrieving order {order_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting order {order_id}: {str(e)}")
            raise Exception(f"Error retrieving order {order_id}: {str(e)}")
    
    def get_orders_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            A list of dictionaries containing order details
        """
        try:
            response = requests.get(
                f"{self.base_url}/order/user/orders",
                headers=self._get_headers(),
                params={'user_id': user_id}
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"Failed to get orders for user {user_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting orders for user {user_id}: {str(e)}")
            return []
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """
        Update the status of an order.
        
        Args:
            order_id: The ID of the order to update
            status: The new status
            
        Returns:
            True if the update is successful, False otherwise
        """
        try:
            response = requests.put(
                f"{self.base_url}/order/orders/{order_id}",
                headers=self._get_headers(),
                json={'status': status}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update order {order_id} status to {status}: {str(e)}")
            return False
    
    def validate_order(self, order_id: str) -> bool:
        """
        Validate that an order exists and is in a valid state for invoicing.
        
        Args:
            order_id: The ID of the order to validate
            
        Returns:
            True if the order is valid, False otherwise
        """
        try:
            order = self.get_order(order_id)
            # Check if the order status is valid for invoicing
            valid_statuses = ['CONFIRMED', 'COMPLETED']
            return order.get('status') in valid_statuses
        except Exception:
            return False
    
    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Get the items in an order.
        
        Args:
            order_id: The ID of the order
            
        Returns:
            A list of dictionaries containing item details
        """
        try:
            order = self.get_order(order_id)
            return order.get('items', [])
        except Exception as e:
            logger.error(f"Failed to get items for order {order_id}: {str(e)}")
            return [] 