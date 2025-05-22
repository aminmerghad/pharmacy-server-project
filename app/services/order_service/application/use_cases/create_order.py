from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from app.services.inventory_service.application.events.stock_release_requested_event import StockReleaseRequestedEvent
from app.services.order_service.application.commands import CreateOrderCommand
from app.services.order_service.application.dtos.order_dto import CreateOrderItemDTO, CreateOrderResponse
from app.services.order_service.application.events import OrderCreatedEvent
from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.entities.order_item import OrderItem
from app.services.order_service.domain.exceptions.order_errors import OrderCreationError, OrderValidationError
from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.domain.value_objects.money import Money
from app.services.order_service.infrastructure.query_services.order_query_service import OrderQueryService
from app.shared.contracts.inventory.stock_check import StockCheckItemContract, StockCheckRequestContract
from decimal import Decimal

@dataclass
class OrderItemDTO:
    product_id: str
    quantity: int
    price: float


class CreateOrderDto(BaseModel):
    order_id: UUID
    items: list[OrderItemDTO]
    status: OrderStatus
    total_amount: float
    created_at: datetime
    consumer_id:Optional[UUID]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

class CreateOrderUseCase:
    def __init__(self, uow: UnitOfWork, order_qr: OrderQueryService):
        self.uow = uow
        self.order_qr = order_qr

    def execute(self, command: CreateOrderCommand) -> CreateOrderResponse:
        # Validate input data
        # self._validate_order_command(command)
        
        # If user_id is provided, check if user is eligible to place orders
        # if command.user_id:
        #     self._check_user_eligibility(command.user_id)
        
            # Check stock availability before creating order
        self._check_stock_level(command)
            
            # Create order items and calculate total
        
        order_items = self._order_item_list(command)
        total_amount = self._calculate_total_amount(order_items)
        
            # Create the order in PENDING status
        order = self._create_order(command, order_items, total_amount)
        try:
                # Publish stock release event
            # self.uow.publish(StockReleaseRequestedEvent(
            #     order_id=order.id,
            #     items=[{
            #         'product_id': str(item.product_id),
            #         'quantity': item.quantity
            #     } for item in command.items]
            # ))
                
            # Publish order created event
            # self.uow.publish(OrderCreatedEvent(
            #     order_id=str(order.id)          
            # ))
                
            # Commit transaction
            self.uow.commit()
            
                # Run post-creation workflows in a separate process/thread
            # self._trigger_post_creation_workflows(order)
                
                # Create DTO for response
            order_dto = self._create_order_dto(order)
            return order_dto
                
        except Exception as e:
                # Rollback transaction in case of error
            self.uow.rollback()
                
            # Re-raise the exception for higher-level handling
            raise OrderCreationError(
                message=f"Failed to create order: {str(e)}",
                status_code=500
            )
    
    def _validate_order_command(self, command: CreateOrderCommand) -> None:
        """Validate order command data"""
        if not command.items or len(command.items) == 0:
            raise OrderValidationError("Order must contain at least one item")
        
        for item in command.items:
            if not item.product_id:
                raise OrderValidationError("Product ID is required for all items")
            if not item.quantity or item.quantity <= 0:
                raise OrderValidationError(f"Invalid quantity for product {item.product_id}")
            if not hasattr(item, 'unit_price') or not item.unit_price:
                raise OrderValidationError(f"Unit price is required for product {item.product_id}")
    
    def _check_user_eligibility(self, user_id: UUID) -> None:
        """Check if user is eligible to place orders"""
        # Example implementation - would connect to user service
        # This is just a placeholder - implement according to your actual user service
        user_service = self.uow.order_adapter_service
        user_eligible = user_service.check_user_eligibility(user_id)
        
        if not user_eligible:
            raise OrderValidationError(f"User {user_id} is not eligible to place orders")
    
    def _create_order(self, command: CreateOrderCommand, order_items: List[OrderItem], total_amount: Decimal):
        """Create order entity and add to repository"""
        # Create order in PENDING status - will be updated based on stock release result
        order = self.uow.order_repository.add(OrderEntity(
            user_id=command.user_id,
            total_amount=total_amount,
            items=order_items,
            notes=command.notes,
            status=OrderStatus.PENDING
        ))


        return order
        
    def _create_order_dto(self, order: OrderEntity):
        """Create DTO from order entity"""

        order_items = [OrderItemDTO(
            product_id=str(item.product_id),
            quantity=item.quantity,
            price=float(item.price.amount)
            ) for item in order.items]
        return CreateOrderDto(
            order_id=order.id,
            status=order.status,
            total_amount=order.total_amount.amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            completed_at=order.completed_at,
            items=order_items,      
            consumer_id=order.user_id     
        )
    
    def _calculate_total_amount(self, order_items: List[OrderItem]) -> Money:
        """Calculate total amount for all items"""
        total= sum(item.quantity * Decimal(str(item.price.amount)) for item in order_items)
        return total
        
    def _check_stock_level(self, command: CreateOrderCommand):
        """Check if stock is available for all items"""
        adapter_service = self.uow.order_adapter_service
        
        stock_check_result = adapter_service.stock_check(
            StockCheckRequestContract(items=[
                StockCheckItemContract(
                    product_id=item.product_id,
                    quantity=item.quantity
                ) for item in command.items
            ])
        )
        is_legit = stock_check_result.is_legit()
        
        if not is_legit:
            raise OrderCreationError(
                message="Stock is not available for some items",
                errors=stock_check_result.model_dump()
            )
        
    def _order_item_list(self, command: CreateOrderCommand):
        """Convert command items to order items"""
        return [
            OrderItem.create(
                price=item.price,
                product_id=item.product_id,
                quantity=item.quantity
            ) for item in command.items
        ]
    
    def _trigger_post_creation_workflows(self, order):
        """Trigger asynchronous post-creation workflows"""
        # These would typically be handled asynchronously to not block the order creation
        try:
            # 1. Send order confirmation email/notification
            self._schedule_notification(order, "ORDER_CREATED")
            
            # 2. Generate invoice/receipt
            self._schedule_document_generation(order, "INVOICE")
            
            # 3. Trigger payment processing if needed
            if hasattr(order, 'payment_method') and order.payment_method:
                self._schedule_payment_processing(order)
            
            # 4. Schedule delivery if applicable
            if hasattr(order, 'delivery_address') and order.delivery_address:
                self._schedule_delivery_planning(order)
            
            # 5. Notify external systems if needed
            self._notify_external_systems(order)
        except Exception as e:
            # Log error but don't fail the order creation
            print(f"Error in post-creation workflows: {str(e)}")
    
    def _schedule_notification(self, order: OrderEntity, notification_type: str) -> None:
        """Schedule notification to be sent asynchronously"""
        # Example implementation - would use a message queue in production
        notification_data = {
            "type": notification_type,
            "order_id": str(order.id),
            "user_id": str(order.user_id) if order.user_id else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would publish to a queue
        self.uow.publish({
            "event_type": "notification.requested",
            "payload": notification_data
        })
    
    def _schedule_document_generation(self, order: OrderEntity, document_type: str) -> None:
        """Schedule document generation asynchronously"""
        # Example implementation
        document_data = {
            "type": document_type,
            "order_id": str(order.id),
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would publish to a queue
        self.uow.publish({
            "event_type": "document.generation.requested",
            "payload": document_data
        })
    
    def _schedule_payment_processing(self, order: OrderEntity) -> None:
        """Schedule payment processing asynchronously"""
        # Example implementation
        payment_data = {
            "order_id": str(order.id),
            "amount": float(order.total_amount),
            "payment_method": order.payment_method if hasattr(order, 'payment_method') else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would publish to a queue
        self.uow.publish({
            "event_type": "payment.processing.requested",
            "payload": payment_data
        })
    
    def _schedule_delivery_planning(self, order: OrderEntity) -> None:
        """Schedule delivery planning asynchronously"""
        # Example implementation
        delivery_data = {
            "order_id": str(order.id),
            "address": order.delivery_address if hasattr(order, 'delivery_address') else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would publish to a queue
        self.uow.publish({
            "event_type": "delivery.planning.requested",
            "payload": delivery_data
        })
    
    def _notify_external_systems(self, order: OrderEntity) -> None:
        """Notify external systems about the new order"""
        # Example implementation - would integrate with external systems
        # This is a placeholder
        pass

    #def excute
        #     # Check stock availability before creating order
        # self._check_stock_level(command)
        
        # # Create the order in PENDING status
        # order = self._create_order(command)
        
        # try:
        #     # Publish stock release event
        #     self.uow.publish(StockReleaseRequestedEvent(
        #         order_id=order.id,
        #         items=[{
        #             'product_id': str(item.product_id),
        #             'quantity': item.quantity
        #         } for item in command.items]
            
        #     ))
            
        #     # # Publish order created event
        #     # self.uow.publish_event(OrderCreatedEvent(
        #     #     order_id=str(order.id)          
        #     # ))
            
        #     # Commit transaction
        #     self.uow.commit()
            
        #     # Create DTO for response
        #     order_dto = self._create_order_dto(order)
        #     return order_dto
            
        # except Exception as e:
        #     # Rollback transaction in case of error
        #     self.uow.rollback()
            
        #     # Re-raise the exception for higher-level handling
        #     raise OrderCreationError(
        #         messege=f"Failed to create order: {str(e)}",
        #         status_code=500
        #     )
    
    
