from typing import Any

from sqlalchemy.orm import Session

from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.order_service.infrastructure.adapters.order_adpter_service import OrderAdapterService
from app.services.order_service.infrastructure.persistence.repositories.order_repository import SQLAlchemyOrderRepository
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session,event_bus: EventBus,acl: UnifiedACL):
        self._session = session
        self._event_bus = event_bus
        self._acl = acl
        self._order_adapter_service = None
        self._order_repository=None
        
    @property
    def order_repository(self):
        if not self._order_repository:
            self._order_repository = SQLAlchemyOrderRepository(self._session)
        return self._order_repository
    @property
    def order_adapter_service(self):
        if not self._order_adapter_service:
            self._order_adapter_service = OrderAdapterService(self._acl)
        return self._order_adapter_service

    def __enter__(self) -> 'SQLAlchemyUnitOfWork':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def refresh(self, instance: Any) -> None:
        self._session.refresh(instance)
    
    def publish(self, event: Any) -> None:
        self._event_bus.publish(event)

# import logging
# from typing import Dict, Any, Optional
# import json

# from sqlalchemy.orm import Session

# from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
# from app.services.order_service.infrastructure.repositories.sqlalchemy_order_repository import SQLAlchemyOrderRepository
# from app.services.order_service.infrastructure.adapters.order_adpter_service import OrderAdapterService
# from app.services.order_service.infrastructure.adapters.event_bus_adapter import EventBusAdapter
# from app.services.order_service.infrastructure.adapters.cache_adapter import CacheAdapter

# logger = logging.getLogger(__name__)

# class SQLAlchemyUnitOfWork(UnitOfWork):
#     """
#     SQLAlchemy implementation of the unit of work pattern for managing transactions.
#     """
    
#     def __init__(self, session_factory, event_bus: EventBusAdapter, cache: CacheAdapter, adapter_service: OrderAdapterService = None):
#         """
#         Initialize the unit of work with a session factory, event bus, and cache adapter.
        
#         Args:
#             session_factory: Factory function for creating SQLAlchemy sessions
#             event_bus: Event bus adapter for publishing events
#             cache: Cache adapter for caching
#             adapter_service: Optional order adapter service
#         """
#         self.session_factory = session_factory
#         self.event_bus = event_bus
#         self.cache = cache
#         self.order_adapter_service = adapter_service
        
#     def __enter__(self):
#         """
#         Begin a new transaction and create a new session.
        
#         Returns:
#             Self
#         """
#         self.session = self.session_factory()
#         self._order_repository = SQLAlchemyOrderRepository(self.session)
        
#         logger.debug("Starting new transaction")
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """
#         End the transaction, rolling back if an exception occurred.
        
#         Args:
#             exc_type: Exception type, if an exception was raised
#             exc_val: Exception value, if an exception was raised
#             exc_tb: Exception traceback, if an exception was raised
#         """
#         if exc_type:
#             logger.error(f"Transaction failed: {exc_val}")
#             self.rollback()
#         else:
#             self.session.close()
            
#         logger.debug("Transaction ended")
    
#     @property
#     def order_repository(self):
#         """
#         Get the order repository.
        
#         Returns:
#             SQLAlchemyOrderRepository instance
#         """
#         return self._order_repository
    
#     def commit(self):
#         """
#         Commit the current transaction.
#         """
#         logger.debug("Committing transaction")
#         try:
#             self.session.commit()
#         except Exception as e:
#             logger.error(f"Error committing transaction: {str(e)}")
#             self.rollback()
#             raise
    
#     def rollback(self):
#         """
#         Roll back the current transaction.
#         """
#         logger.debug("Rolling back transaction")
#         self.session.rollback()
    
#     def publish(self, event: Dict[str, Any]):
#         """
#         Publish an event to the event bus.
        
#         Args:
#             event: Event to publish, as a dictionary
#         """
#         try:
#             logger.info(f"Publishing event: {event.get('type')}")
#             logger.debug(f"Event details: {json.dumps(event)}")
#             self.event_bus.publish(event)
#         except Exception as e:
#             logger.error(f"Error publishing event: {str(e)}")
#             # We don't want to break the transaction if event publishing fails
#             # But we might want to log and monitor these failures
    
#     def clear_cache(self, cache_key: Optional[str] = None):
#         """
#         Clear the cache, optionally for a specific key.
        
#         Args:
#             cache_key: Optional cache key to clear. If None, clears all order-related caches.
#         """
#         try:
#             if cache_key:
#                 logger.debug(f"Clearing cache for key: {cache_key}")
#                 self.cache.delete(cache_key)
#             else:
#                 logger.debug("Clearing all order-related caches")
#                 self.cache.delete_pattern("order:*")
#         except Exception as e:
#             logger.error(f"Error clearing cache: {str(e)}")
#             # We don't want to break the transaction if cache clearing fails
    
#     def collect_new_events(self):
#         """
#         Collect new events from the aggregate roots in the repository.
        
#         Yields:
#             Events from aggregates
#         """
#         for order in self._order_repository.seen:
#             while order.events:
#                 yield order.events.pop(0) 