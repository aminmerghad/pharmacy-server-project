from abc import ABC, abstractmethod
from typing import Any

from app.services.order_service.domain.interfaces.order_repository import OrderRepository
from app.services.order_service.infrastructure.adapters.order_adpter_service import OrderAdapterService

class UnitOfWork(ABC):
    order_repository: OrderRepository
    order_adapter_service: OrderAdapterService

    @abstractmethod
    def __enter__(self) -> 'UnitOfWork':
        """Enter the context manager"""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction"""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction"""
        pass

    @abstractmethod
    def refresh(self, instance: Any) -> None:
        """Refresh an instance from the database"""
        pass

    def collect_new_events(self) :
        """Collect all new domain events from aggregates"""
        for order in self.orders.seen:
            while order.events:
                yield order.events.pop(0)    
    def publish(self,event:any):
        pass
