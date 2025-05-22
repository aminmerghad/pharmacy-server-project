from uuid import UUID

from app.services.order_service.application.events.order_updated_event import OrderUpdatedEvent
from app.services.order_service.application.events.stock_release_processed_event import StockReleaseProcessedEvent
from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.order_service.domain.value_objects.order_status import OrderStatus
import logging

logger = logging.getLogger(__name__)

class OrderEventHandler:
    """
    Event handler for order-related events.
    """
    
    def __init__(self, uow: UnitOfWork):
        """
        Initialize the event handler with a unit of work.
        
        Args:
            uow: Unit of work for transaction management
        """
        self._uow = uow
    
    def handle_stock_release_processed(self, event: StockReleaseProcessedEvent):
        """
        Handle stock release processed event from inventory service.
        Updates order status based on stock release results.
        
        Args:
            event: StockReleaseProcessedEvent containing the results
        """
        order_id = event.order_id
        success = event.success
        items = event.items
        
        try:
            with self._uow:
                # Get order
                order = self._uow.order_repository.get_by_id(UUID(order_id))
                
                if not order:
                    # Log error: Order not found
                    logger.error(f"Order {order_id} not found when processing stock release event")
                    return
                
                if success:
                    # Update order status to confirmed
                    order.status = OrderStatus.CONFIRMED
                    # You might want to add additional logic here for confirmed orders
                    
                    # Optionally publish order confirmed event
                    self._uow.publish({
                        "type": "order.confirmed",
                        "order_id": order_id,
                        "timestamp": event.timestamp
                    })
                else:
                    # Update order status to failed
                    order.status = OrderStatus.FAILED
                    
                    # Create error messages for failed items
                    error_messages = []
                    for item in items:
                        if not item.get('success', False):
                            product_id = item.get('product_id')
                            message = item.get('message')
                            error_messages.append(f"Product {product_id}: {message}")
                    
                    # Set failure reason
                    order.failure_reason = "Stock release failed: " + ", ".join(error_messages)
                    
                    # Optionally publish order failed event
                    self._uow.publish({
                        "type": "order.failed",
                        "order_id": order_id,
                        "reason": order.failure_reason,
                        "timestamp": event.timestamp
                    })
                
                # Update order in repository
                self._uow.order_repository.update(order)
                self._uow.commit()
                
                logger.info(f"Order {order_id} status updated to {order.status} after stock release")
                
        except Exception as e:
            # Ensure transaction is rolled back
            self._uow.rollback()
            # Log error
            logger.error(f"Error handling stock release processed event: {str(e)}", exc_info=True)
            
    def handle_order_updated_event(self, event: OrderUpdatedEvent):
        """
        Handle order updated event.
        Performs post-update actions based on the new order status.
        
        Args:
            event: OrderUpdatedEvent containing the updated order information
        """
        order_id = event.order_id
        
        try:
            with self._uow:
                # Get order
                order = self._uow.order_repository.get_by_id(UUID(order_id))
                
                if not order:
                    logger.error(f"Order {order_id} not found when processing order updated event")
                    return
                
                # Perform different actions based on new status
                if order.status == OrderStatus.CONFIRMED:
                    # Handle confirmed order - e.g., notify customer, prepare for fulfillment
                    logger.info(f"Order {order_id} confirmed, triggering fulfillment process")
                    self._trigger_fulfillment_process(order)
                    
                elif order.status == OrderStatus.COMPLETED:
                    # Handle completed order - e.g., notify customer, update inventory, trigger analytics
                    logger.info(f"Order {order_id} completed, triggering completion workflows")
                    self._trigger_completion_workflows(order)
                    
                elif order.status == OrderStatus.CANCELLED:
                    # Handle cancelled order - e.g., release inventory, issue refund if needed
                    logger.info(f"Order {order_id} cancelled, triggering cancellation workflows")
                    self._trigger_cancellation_workflows(order)
                    
                elif order.status == OrderStatus.FAILED:
                    # Handle failed order - e.g., notify customer of failure, suggest alternatives
                    logger.info(f"Order {order_id} failed, triggering failure handling")
                    self._trigger_failure_handling(order)
                
                # No changes to save in this method - we're just reacting to the event
                # Commit any changes that might have been made
                self._uow.commit()
                
        except Exception as e:
            # Ensure transaction is rolled back
            self._uow.rollback()
            # Log error
            logger.error(f"Error handling order updated event: {str(e)}", exc_info=True)
            
    def _trigger_fulfillment_process(self, order):
        """
        Trigger the fulfillment process for a confirmed order.
        This might involve notifying warehouse staff, scheduling delivery, etc.
        """
        # This is where you would implement the actual fulfillment logic
        # For example, publishing a message to a fulfillment queue
        try:
            self._uow.publish({
                "type": "fulfillment.requested",
                "order_id": str(order.id),
                "timestamp": str(order.updated_at)
            })
            logger.info(f"Fulfillment requested for order {order.id}")
        except Exception as e:
            logger.error(f"Error triggering fulfillment for order {order.id}: {str(e)}")
            # We don't raise the exception here to avoid failing the entire event handler
    
    def _trigger_completion_workflows(self, order):
        """
        Trigger workflows for a completed order.
        This might involve sending a thank you email, updating customer purchase history, etc.
        """
        try:
            # Update customer purchase history
            self._uow.publish({
                "type": "customer.purchase.completed",
                "order_id": str(order.id),
                "user_id": str(order.user_id),
                "total_amount": str(order.total_amount),
                "timestamp": str(order.completed_at or order.updated_at)
            })
            
            # Send notification
            self._uow.publish({
                "type": "notification.order.completed",
                "order_id": str(order.id),
                "user_id": str(order.user_id),
                "timestamp": str(order.completed_at or order.updated_at)
            })
            
            logger.info(f"Completion workflows triggered for order {order.id}")
        except Exception as e:
            logger.error(f"Error triggering completion workflows for order {order.id}: {str(e)}")
    
    def _trigger_cancellation_workflows(self, order):
        """
        Trigger workflows for a cancelled order.
        This might involve releasing inventory, issuing refunds, etc.
        """
        try:
            # Release inventory
            self._uow.publish({
                "type": "inventory.release.requested",
                "order_id": str(order.id),
                "items": [{"product_id": str(item.product_id), "quantity": item.quantity} for item in order.items],
                "timestamp": str(order.updated_at)
            })
            
            # Send notification
            self._uow.publish({
                "type": "notification.order.cancelled",
                "order_id": str(order.id),
                "user_id": str(order.user_id),
                "timestamp": str(order.updated_at)
            })
            
            logger.info(f"Cancellation workflows triggered for order {order.id}")
        except Exception as e:
            logger.error(f"Error triggering cancellation workflows for order {order.id}: {str(e)}")
    
    def _trigger_failure_handling(self, order):
        """
        Handle a failed order.
        This might involve notifying the customer, suggesting alternatives, etc.
        """
        try:
            # Send notification
            self._uow.publish({
                "type": "notification.order.failed",
                "order_id": str(order.id),
                "user_id": str(order.user_id),
                "reason": getattr(order, "failure_reason", "Unknown reason"),
                "timestamp": str(order.updated_at)
            })
            
            logger.info(f"Failure handling triggered for order {order.id}")
        except Exception as e:
            logger.error(f"Error triggering failure handling for order {order.id}: {str(e)}")