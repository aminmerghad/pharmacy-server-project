from app.services.order_service.application.commands.cancel_order_command import CancelOrderCommand
from app.services.order_service.application.dtos.order_dto import OrderDTO
from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.exceptions.order_errors import (
    OrderNotFoundError,
    OrderValidationError,
    OrderCancellationError
)
from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.order_service.infrastructure.query_services.order_query_service import OrderQueryService

class CancelOrderUseCase:
    def __init__(self, uow: UnitOfWork, query_service: OrderQueryService):
        self._uow = uow
        self._query_service = query_service

    def execute(self, command: CancelOrderCommand) -> OrderDTO:
        with self._uow:
            # Get order
            order = self._uow.order_repository.get(command.order_id)
            if not order:
                raise OrderNotFoundError(f"Order {command.order_id} not found")
            is_admin=self.order_adapter.get_admin(command.user_id)
            if not order.can_be_modified_by(command.user_id) or not is_admin:
                raise OrderCancellationError(
                        "You don't have permission"
                    )

            try:
                # Check if order can be cancelled
                if not order.can_cancel() or not is_admin:
                    raise OrderCancellationError(
                        "Order cannot be cancelled in its current state"
                    )

                # Cancel order and update notes
                order.cancel()
                if command.reason:
                    order.notes = f"Cancelled: {command.reason}"

                # Save changes
                cancelled_order = self._uow.order_repository.update(order)
                self._uow.commit()
                
                # Get updated order from query service for DTO creation
                order_model = self._query_service.get_order_by_id(command.order_id)
                return self._query_service._mapper.to_dto(order_model)

            except Exception as e:
                self._uow.rollback()
                raise OrderValidationError(f"Failed to cancel order: {str(e)}") 