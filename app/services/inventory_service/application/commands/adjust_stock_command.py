from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator

from app.services.inventory_service.domain.enums.movement_type import MovementType


class AdjustStockCommand(BaseModel):
    """
    Command for adjusting inventory stock levels with proper tracking.
    
    This command captures the details needed for a stock adjustment, including
    the reason for the adjustment for audit purposes.
    """
    inventory_id: UUID
    quantity: int  # Positive for increase, negative for decrease
    reason: str
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    
    @validator("quantity")
    def validate_quantity(cls, value):
        """Validate that quantity is not zero"""
        if value == 0:
            raise ValueError("Adjustment quantity cannot be zero")
        return value
        
    @property
    def movement_type(self) -> MovementType:
        """Determine the movement type based on the quantity direction"""
        return (
            MovementType.ADJUSTMENT_INCREASE if self.quantity > 0
            else MovementType.ADJUSTMENT_DECREASE
        )