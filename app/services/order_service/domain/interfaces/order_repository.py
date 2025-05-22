from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.value_objects.order_status import OrderStatus

class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: OrderEntity) -> OrderEntity:
        """Add a new order"""
        pass

    @abstractmethod
    def get(self, order_id: UUID) -> Optional[OrderEntity]:
        """Get an order by ID"""
        pass

    @abstractmethod
    def update(self, order: OrderEntity) -> OrderEntity:
        """Update an existing order"""
        pass

    @abstractmethod
    def delete(self, order_id: UUID) -> None:
        """Delete an order"""
        pass

    @abstractmethod
    def get_by_user(
        self,
        user_id: UUID,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OrderEntity]:
        """Get orders for a user with optional filters"""
        pass

    @abstractmethod
    def get_by_status(
        self,
        status: OrderStatus,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OrderEntity]:
        """Get orders by status"""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OrderEntity]:
        """Search orders"""
        pass

    @abstractmethod
    def exists(self, order_id: UUID) -> bool:
        """Check if an order exists"""
        pass 