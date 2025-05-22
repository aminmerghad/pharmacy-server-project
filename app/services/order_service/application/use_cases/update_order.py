from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from app.services.order_service.application.commands.update_order_command import UpdateOrderCommand
from app.services.order_service.application.dtos.order_dto import OrderDTO
from app.services.order_service.application.events.order_updated_event import OrderUpdatedEvent
from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.exceptions.order_errors import (
    OrderNotFoundError,
    OrderValidationError
)
from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.infrastructure.query_services.order_query_service import OrderQueryService
class UpdateOrderDto(BaseModel):
    order_id: UUID
    new_status: OrderStatus
    old_status: OrderStatus

    
class UpdateOrderUseCase:
    def __init__(self, uow: UnitOfWork, query_service: OrderQueryService):
        self._uow = uow
        self._query_service = query_service

    def execute(self, command: UpdateOrderCommand) -> UpdateOrderDto:
        
        # Get order
        order = self._get_order_or_not_found(command.id)
        old_status=order.status

        # Update status if provided
        order.update_status(command.status)             
        
        # Save changes
        updated_order = self._uow.order_repository.update(order)
                
        # Publish order updated event
        self._uow.publish(OrderUpdatedEvent(order_id=order.id))
                
        # Commit transaction
        self._uow.commit() 

        return UpdateOrderDto(
            order_id=updated_order.id, 
            new_status=updated_order.status,
            old_status=old_status
            )
            
            
    def _get_order_or_not_found(self,order_id:UUID) -> OrderEntity: 
        order = self._uow.order_repository.get(order_id)
        
        if not order:
            raise OrderNotFoundError()
        return order