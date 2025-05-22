from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
import logging

from app.dataBase import Database
from app.services.inventory_service.infrastructure.query_services.inventory_query_service import InventoryQueryService
from app.services.order_service.application.commands.cancel_order_command import CancelOrderCommand
from app.services.order_service.application.commands.create_order_command import CreateOrderCommand
from app.services.order_service.application.commands.update_order_command import UpdateOrderCommand
from app.services.order_service.application.dtos.order_dto import (
    CreateOrderResponse,
    OrderDTO,
    OrderSummaryDTO,
    OrderFilterDTO,
    CreateOrderDTO
)
from app.services.order_service.application.event_handlers.order_event_handlers import OrderEventHandler
from app.services.order_service.application.events.order_updated_event import OrderUpdatedEvent
from app.services.order_service.application.events.stock_release_processed_event import StockReleaseProcessedEvent
from app.services.order_service.application.events.order_created_event import OrderCreatedEvent
from app.services.order_service.application.use_cases.cancel_order import CancelOrderUseCase
from app.services.order_service.application.use_cases.create_order import CreateOrderUseCase
from app.services.order_service.application.use_cases.update_order import UpdateOrderUseCase
from app.services.order_service.domain.exceptions.order_errors import (
    InvalidOrderStatusTransition,
    OrderNotFoundError,
    OrderValidationError,
    OrderCreationError,
    OrderCancellationError
)
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.infrastructure.persistence.mappers.order_mapper import OrderMapper
from app.services.order_service.infrastructure.query_services.order_query_service import OrderQueryService
from app.services.order_service.infrastructure.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

# Configure logger
logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: Database, event_bus: EventBus, acl: UnifiedACL):
        self._db_session = db.get_session()
        self._acl = acl
        self._event_bus = event_bus
        self._init_resources()
        self._register_event_handlers()
        logger.info("Order service initialized")

    def _init_resources(self):
        self._uow = SQLAlchemyUnitOfWork(self._db_session, self._event_bus, self._acl)
        self._query_service = OrderQueryService(self._db_session)
        self._create_order_use_case = CreateOrderUseCase(self._uow, self._query_service)
        self._update_order_use_case = UpdateOrderUseCase(self._uow, self._query_service)
        self._cancel_order_use_case = CancelOrderUseCase(self._uow, self._query_service)
        self._mapper = OrderMapper()
        self._event_handler = OrderEventHandler(self._uow)
        
    def _register_event_handlers(self):
        """Register event handlers with the event bus."""
        if self._event_bus:
            self._event_bus.subscribe(StockReleaseProcessedEvent, self._event_handler.handle_stock_release_processed)
            self._event_bus.subscribe(OrderUpdatedEvent, self._event_handler.handle_order_updated_event)           
            logger.info("Event handlers registered successfully")
            
    def create_order(self, command: CreateOrderCommand) -> CreateOrderResponse:
        """Create a new order"""
        logger.info(f"Creating new order for user {command.user_id}")
        try:
            response = self._create_order_use_case.execute(command)
            # Publish order created event to event bus
            # self._event_bus.publish(OrderCreatedEvent(order_id=str(response.order.id)))
            logger.info(f"Order created successfully")
            # Invalidate caches that might contain old data
            # self._query_service.invalidate_cache(f"user_orders_{command.user_id}")
            # self._query_service.invalidate_cache("all_orders")
            return response
        except OrderValidationError as e:
            logger.error(f"Order validation error: {str(e)}")
            self._uow.rollback()
            raise e
        except OrderCreationError as e:
            logger.error(f"Order creation error: {str(e)}")
            self._uow.rollback()
            raise e
        except Exception as e:
            logger.error(f"Unexpected error creating order: {str(e)}", exc_info=True)
            self._uow.rollback()
            raise OrderCreationError(message=f"Failed to create order: {str(e)}", status_code=500)
    
    def create_batch_orders(self, commands: List[CreateOrderCommand]) -> List[Dict]:
        """Create multiple orders in a batch operation"""
        logger.info(f"Creating batch of {len(commands)} orders")
        results = []
        
        for command in commands:
            try:
                result = self.create_order(command)
                results.append({
                    "status": "success", 
                    "order_id": str(result.order.id),
                    "message": f"Order created successfully"
                })
            except Exception as e:
                logger.error(f"Failed to create order in batch: {str(e)}")
                results.append({
                    "status": "error", 
                    "user_id": str(command.user_id) if command.user_id else None,
                    "error": str(e)
                })
                
        return results
    def update_order_status(self, command: UpdateOrderCommand) :
        """Update order status"""
        logger.info(f"Updating order {command.id} status to {command.status}")
        try:
            result = self._update_order_use_case.execute(command)     
            
                # Invalidate caches
                # self._query_service.invalidate_cache(f"order_{command.id}")
                # Clear the lru_cache for this specific order
                # self.get_order.cache_clear()
                
            logger.info(f"Order {command.id} status updated successfully")
            return result
        except OrderNotFoundError as e:
            logger.error(f"Order not found: {str(e)}")
            self._uow.rollback()
            raise e
        except InvalidOrderStatusTransition as e:
            logger.error(f"Invalid status transition: {str(e)}")
            self._uow.rollback()
            raise e        
        except Exception as e:
            logger.error(f"Unexpected error updating order: {str(e)}", exc_info=True)
            self._uow.rollback()
            raise OrderValidationError(f"Failed to update order: {str(e)}")
    
    def cancel_order(self, command: CancelOrderCommand) -> dict:
        """Cancel an order"""
        logger.info(f"Cancelling order {command.order_id}")
        try:
            with self._uow:
                result = self._cancel_order_use_case.execute(command)
                self._uow.commit()
                
                # Invalidate caches
                self._query_service.invalidate_cache(f"order_{command.order_id}")
                self.get_order.cache_clear()
                
                logger.info(f"Order {command.order_id} cancelled successfully")
                return result.to_dict()
        except OrderNotFoundError as e:
            logger.error(f"Order not found: {str(e)}")
            self._uow.rollback()
            raise e
        except OrderValidationError as e:
            logger.error(f"Order validation error: {str(e)}")
            self._uow.rollback()
            raise e
        except OrderCancellationError as e:
            logger.error(f"Order cancellation error: {str(e)}")
            self._uow.rollback()
            raise e
        except Exception as e:
            logger.error(f"Unexpected error cancelling order: {str(e)}", exc_info=True)
            self._uow.rollback()
            raise OrderValidationError(f"Failed to cancel order: {str(e)}")
    # @lru_cache(maxsize=100)  # Cache frequently accessed orders
    def get_order(self, order_id: UUID) -> Optional[dict]:
        """Get order by ID"""
        try:
            order = self._query_service.get_order_by_id(order_id)
            if not order:
                logger.info(f"Order {order_id} not found")
                return None
            return self._mapper.to_dto(order).to_dict()
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise e
    
    def get_orders(self, filter_dto: OrderFilterDTO) -> List[OrderSummaryDTO]:
        """Get filtered and paginated orders"""
        try:
            return self._query_service.get_orders_by_filter(filter_dto)
        except Exception as e:
            logger.error(f"Error filtering orders: {str(e)}")
            raise e
    
    
    
    
    
    def get_user_orders(self, user_id: UUID, page: int = 1, per_page: int = 10) -> List[dict]:
        """Get all orders for a specific user with pagination"""
        try:
            orders = self._query_service.get_orders_by_user_id(user_id, page, per_page)
            return [self._mapper.to_dto(order).to_dict() for order in orders]
        except Exception as e:
            logger.error(f"Error fetching orders for user {user_id}: {str(e)}")
            raise e
     
    def get_user_order_stats(self, user_id: UUID) -> dict:
        """Get order statistics for a user"""
        try:
            return self._query_service.get_user_order_stats(user_id)
        except Exception as e:
            logger.error(f"Error fetching order stats for user {user_id}: {str(e)}")
            raise e

    def get_order_history(self, user_id: UUID, limit: int = 10) -> List[OrderSummaryDTO]:
        """Get user's order history"""
        try:
            return self._query_service.get_order_history(user_id, limit)
        except Exception as e:
            logger.error(f"Error fetching order history for user {user_id}: {str(e)}")
            raise e
            
    def get_order_status_summary(self) -> Dict[str, int]:
        """Get a summary count of orders by status"""
        try:
            result = {}
            for status in OrderStatus:
                filter_dto = OrderFilterDTO(status=status.value)
                orders, count = self._query_service.get_orders_by_filter(filter_dto)
                result[status.value] = count
            return result
        except Exception as e:
            logger.error(f"Error getting order status summary: {str(e)}")
            raise e
            
    def get_daily_order_stats(self, days: int = 30) -> List[Dict]:
        """Get daily order statistics for the last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            daily_stats = []
            current_date = start_date
            
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                
                # Create filter for this day
                filter_dto = OrderFilterDTO(
                    start_date=current_date,
                    end_date=next_date,
                    page=1,
                    per_page=1000
                )
                
                # Get orders for this day
                orders, total = self._query_service.get_orders_by_filter(filter_dto)
                
                # Calculate total revenue
                total_revenue = sum(order.total_amount for order in orders) if orders else 0
                
                # Add stats for this day
                daily_stats.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "order_count": total,
                    "total_revenue": float(total_revenue)
                })
                
                # Move to next day
                current_date = next_date
                
            return daily_stats
        except Exception as e:
            logger.error(f"Error generating daily order stats: {str(e)}")
            raise e
    
    def export_orders(self, filter_dto: OrderFilterDTO, format: str = "json") -> Dict:
        """Export orders based on filter criteria"""
        try:
            orders, total = self._query_service.get_orders_by_filter(filter_dto)
            
            if format.lower() == "csv":
                # Prepare CSV format
                result = {
                    "format": "csv",
                    "total_records": total,
                    "headers": ["Order ID", "User ID", "Status", "Total Amount", "Items Count", "Created At"],
                    "data": [
                        [
                            str(order.id),
                            str(order.user_id),
                            order.status,
                            str(order.total_amount),
                            str(order.items_count),
                            order.created_at.isoformat()
                        ] for order in orders
                    ]
                }
            else:
                # Default JSON format
                result = {
                    "format": "json",
                    "total_records": total,
                    "data": [self._to_dict(order) for order in orders]
                }
                
            return result
        except Exception as e:
            logger.error(f"Error exporting orders: {str(e)}")
            raise e
            
    def duplicate_order(self, order_id: UUID, user_id: UUID = None) -> CreateOrderResponse:
        """Create a duplicate of an existing order"""
        try:
            logger.info(f"Duplicating order {order_id}")
            
            # Get original order
            order = self._query_service.get_order_by_id(order_id)
            if not order:
                raise OrderNotFoundError(f"Order {order_id} not found")
                
            # Convert to entity to access items
            order_entity = self._mapper.to_entity(order)
                
            # Create command for new order
            command = CreateOrderCommand(
                user_id=user_id or order_entity.user_id,
                items=[{
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.price.amount)
                } for item in order_entity.items],
                notes=f"Duplicated from order {order_id}"
            )
            
            # Create the new order
            return self.create_order(command)
        except Exception as e:
            logger.error(f"Error duplicating order {order_id}: {str(e)}")
            if isinstance(e, OrderNotFoundError):
                raise e
            raise OrderCreationError(message=f"Failed to duplicate order: {str(e)}")
    
    def archive_orders(self, days: int = 90) -> int:
        """Archive orders older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get orders older than cutoff date
            filter_dto = OrderFilterDTO(
                end_date=cutoff_date,
                per_page=1000  # Process in chunks
            )
            
            orders, total = self._query_service.get_orders_by_filter(filter_dto)
            archived_count = 0
            
            # For each order, mark as archived
            for order in orders:
                try:
                    # In a real implementation, you would move these to an archive table
                    # or set an "archived" flag. This is just an example.
                    command = UpdateOrderCommand(
                        id=order.id,
                        status=OrderStatus.ARCHIVED if hasattr(OrderStatus, "ARCHIVED") else OrderStatus.COMPLETED,
                        notes=f"Archived automatically on {datetime.now().isoformat()}"
                    )
                    self.update_order_status(command)
                    archived_count += 1
                except Exception as e:
                    logger.error(f"Error archiving order {order.id}: {str(e)}")
                    continue
                    
            logger.info(f"Archived {archived_count} orders older than {days} days")
            return archived_count
        except Exception as e:
            logger.error(f"Error archiving old orders: {str(e)}")
            raise e
    # def search_orders(self, query: str, status: Optional[str] = None, page: int = 1, per_page: int = 10) -> List[OrderSummaryDTO]:
    #     """Search orders with pagination"""
    #     try:
    #         order_status = OrderStatus(status) if status else None
    #         return self._query_service.search_orders(query, order_status, page, per_page)
    #     except Exception as e:
    #         logger.error(f"Error searching orders: {str(e)}")
    #         raise e
    # def health_check(self) -> Dict[str, Any]:
    #     """Check the health of the order service and its dependencies"""
    #     health = {
    #         "status": "healthy",
    #         "db_connection": "ok",
    #         "dependencies": {},
    #         "timestamp": datetime.now().isoformat()
    #     }
        
    #     try:
    #         # Check database connection by running a simple query
    #         self._query_service.get_all_orders(page=1, per_page=1)
    #     except Exception as e:
    #         health["status"] = "unhealthy"
    #         health["db_connection"] = f"error: {str(e)}"
            
    #     # Check inventory service connection
    #     try:
    #         # This would need to be implemented based on your actual inventory service
    #         # inventory_status = self._uow.order_adapter_service.check_inventory_service()
    #         health["dependencies"]["inventory"] = "ok"
    #     except Exception as e:
    #         health["dependencies"]["inventory"] = f"error: {str(e)}"
            
    #     return health
    
    # def refresh_cache(self):
    #     """Refresh all caches"""
    #     logger.info("Refreshing order service caches")
    #     self._query_service.invalidate_cache()
    #     self.get_order.cache_clear()
        
   
     
