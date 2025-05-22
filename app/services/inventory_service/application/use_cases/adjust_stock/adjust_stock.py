from uuid import UUID

from app.services.inventory_service.application.commands.adjust_stock_command import AdjustStockCommand
from app.services.inventory_service.application.commands.record_movement_command import RecordMovementCommand
from app.services.inventory_service.application.use_cases.adjust_stock.output_dto import AdjustStockOutputDto
from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
from app.services.inventory_service.domain.exceptions.inventory_errors import InventoryNotFoundError
from app.services.inventory_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork


class AdjustStockUseCase:
    """
    Use case for adjusting inventory stock levels.
    
    This use case handles stock adjustments with proper auditing and
    validation to ensure inventory integrity.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
    
    def execute(self, command: AdjustStockCommand) -> AdjustStockOutputDto:
        """
        Execute the stock adjustment operation.
        
        Args:
            command: The adjustment command with inventory id, quantity and reason
            
        Returns:
            DTO with the result of the adjustment operation
            
        Raises:
            InventoryNotFoundError: If the inventory item doesn't exist
            ValueError: If the adjustment would result in invalid stock levels
        """
        try:
            with self._uow:
                # Get the inventory item
                inventory_repo = self._uow.inventory_repository
                inventory = inventory_repo.get_by_id(command.inventory_id)
                
                if not inventory:
                    raise InventoryNotFoundError(
                        f"Inventory with ID {command.inventory_id} not found",
                        error={"inventory_id": str(command.inventory_id)}
                    )
                
                # Store the original quantity for the response
                original_quantity = inventory.quantity
                
                # Apply the adjustment
                inventory.adjust_stock(
                    quantity=command.quantity,
                    reason=command.reason,
                    movement_type=command.movement_type
                )
                
                # Update inventory
                inventory = inventory_repo.update(inventory)
                
                # Record the movement
                movement_command = RecordMovementCommand(
                    inventory_id=command.inventory_id,
                    quantity=abs(command.quantity),  # Always positive in the movement record
                    movement_type=command.movement_type,
                    reason=command.reason,
                    created_by=command.created_by
                )
                
                # Use the existing stock movement repository
                movement = self._uow.stock_movement_repository.add(
                    self._create_movement_entity(movement_command)
                )
                
                self._uow.commit()
                
                # Return the result
                return AdjustStockOutputDto(
                    inventory_id=inventory.id,
                    product_id=inventory.product_id,
                    previous_quantity=original_quantity,
                    adjustment_quantity=command.quantity,
                    new_quantity=inventory.quantity,
                    reason=command.reason,
                    movement_id=movement.id
                )
                
        except Exception as e:
            self._uow.rollback()
            raise e
    
    def _create_movement_entity(self, command: RecordMovementCommand):
        """
        Create a stock movement entity from the command.
        
        This helper method creates a movement entity from the command
        to record the stock adjustment.
        """
        from app.services.inventory_service.domain.entities.stock_movement_entity import StockMovementEntity
        
        return StockMovementEntity(
            inventory_id=command.inventory_id,
            quantity=command.quantity,
            movement_type=command.movement_type,
            reason=command.reason,
            created_by=command.created_by
        ) 