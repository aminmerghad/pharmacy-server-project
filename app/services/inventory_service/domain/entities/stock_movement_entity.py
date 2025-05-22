from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.services.inventory_service.domain.enums.movement_type import MovementType


class StockMovementEntity(BaseModel):
    """Entity representing a movement of stock in the inventory system"""
    id: Optional[UUID] = None
    inventory_id: UUID
    quantity: int  
    movement_type: MovementType
    reference_id: Optional[UUID] = None  # Order ID, Transfer ID, etc.
    batch_number: Optional[str] = None
    reason: Optional[str] = None  
    created_by: Optional[UUID] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    
    def is_positive_movement(self) -> bool:
        """Check if this movement increases inventory quantity"""
        return self.movement_type in [
            MovementType.RECEIVED, 
            MovementType.RETURNED,
            MovementType.ADJUSTMENT_INCREASE
        ]
    
    def is_negative_movement(self) -> bool:
        """Check if this movement decreases inventory quantity"""
        return self.movement_type in [
            MovementType.DISPENSED, 
            MovementType.EXPIRED,
            MovementType.DAMAGED,
            MovementType.TRANSFERRED_OUT,
            MovementType.ADJUSTMENT_DECREASE
        ]
    
    def get_quantity_effect(self) -> int:
        """Get the effect this movement has on inventory quantity (positive or negative)"""
        return self.quantity if self.is_positive_movement() else -self.quantity
    
    def validate(self) -> bool:
        """Validate that the movement data is valid"""
        if self.quantity <= 0:
            return False
            
        # Reference ID is required for certain movement types
        if self.movement_type in [MovementType.DISPENSED, MovementType.TRANSFERRED_OUT, MovementType.RETURNED] and not self.reference_id:
            return False
            
        # Reason is required for adjustments
        if self.movement_type in [MovementType.ADJUSTMENT_INCREASE, MovementType.ADJUSTMENT_DECREASE] and not self.reason:
            return False
            
        return True 