from typing import Optional
from uuid import UUID

from app.services.inventory_service.application.commands.record_movement_command import RecordMovementCommand
from app.services.inventory_service.domain.entities.stock_movement_entity import StockMovementEntity
from app.services.inventory_service.domain.enums.movement_type import MovementType
from app.services.inventory_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork


class RecordMovementUseCase:
    """
    Use case for recording stock movements in the inventory system.
    
    This use case handles the business logic for tracking inventory movements,
    ensuring that all movements are properly validated and recorded.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
    
    def execute(self, command: RecordMovementCommand) -> StockMovementEntity:
        """
        Record a stock movement in the inventory system.
        
        Args:
            command: The command containing movement details
            
        Returns:
            The created stock movement entity
            
        Raises:
            ValueError: If the movement data is invalid
        """
        # Create the movement entity
        movement = StockMovementEntity(
            inventory_id=command.inventory_id,
            quantity=command.quantity,
            movement_type=command.movement_type,
            reference_id=command.reference_id,
            batch_number=command.batch_number,
            reason=command.reason,
            created_by=command.created_by
        )
        
        # Validate the movement
        if not movement.validate():
            raise ValueError("Invalid stock movement data")
        
        # Persist the movement
        with self._uow:
            # Get the inventory to update
            inventory_repo = self._uow.inventory_repository
            inventory = inventory_repo.get_by_id(command.inventory_id)
            
            if not inventory:
                raise ValueError(f"Inventory with ID {command.inventory_id} not found")
            
            # Update inventory quantity based on movement type
            quantity_effect = movement.get_quantity_effect()
            
            # For negative movements, ensure there's enough stock
            if quantity_effect < 0 and abs(quantity_effect) > inventory.quantity:
                raise ValueError(f"Insufficient stock. Available: {inventory.quantity}, Requested: {abs(quantity_effect)}")
            
            # Record the movement
            movement = self._uow.stock_movement_repository.add(movement)
            
            # Update inventory quantity
            inventory.quantity += quantity_effect
            inventory_repo.update(inventory)
            
            self._uow.commit()
            
        return movement 