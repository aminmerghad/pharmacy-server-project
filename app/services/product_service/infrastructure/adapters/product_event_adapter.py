from datetime import datetime, timezone
from typing import Dict, Any
from uuid import UUID

from app.shared.application.events.event_bus import EventBus
from app.services.product_service.domain.entities.product_entity import ProductEntity


class ProductEventAdapter:
    """
    Adapter for publishing product-related events.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the adapter with an event bus.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self._event_bus = event_bus
    
    def publish_product_created(self, product: ProductEntity) -> None:
        """
        Publish a product created event.
        
        Args:
            product: The created product entity
        """
        self._event_bus.publish("product.created", {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "category_id": str(product.category_id) if product.category_id else None,
            "status": product.status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def publish_product_updated(self, product: ProductEntity) -> None:
        """
        Publish a product updated event.
        
        Args:
            product: The updated product entity
        """
        self._event_bus.publish("product.updated", {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "category_id": str(product.category_id) if product.category_id else None,
            "status": product.status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def publish_product_deleted(self, product_id: UUID, product_name: str) -> None:
        """
        Publish a product deleted event.
        
        Args:
            product_id: The ID of the deleted product
            product_name: The name of the deleted product
        """
        self._event_bus.publish("product.deleted", {
            "id": str(product_id),
            "name": product_name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def publish_product_status_changed(self, product_id: UUID, product_name: str, 
                                      old_status: str, new_status: str) -> None:
        """
        Publish a product status changed event.
        
        Args:
            product_id: The ID of the product
            product_name: The name of the product
            old_status: The previous status
            new_status: The new status
        """
        self._event_bus.publish("product.status_changed", {
            "id": str(product_id),
            "name": product_name,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }) 