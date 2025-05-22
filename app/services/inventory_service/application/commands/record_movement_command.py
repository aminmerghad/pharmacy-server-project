from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.services.inventory_service.domain.enums.movement_type import MovementType


class RecordMovementCommand(BaseModel):
    """
    Command for recording a stock movement in the inventory system.
    
    This command includes all the necessary data to track a stock movement,
    including reference information for audit purposes.
    """
    inventory_id: UUID
    quantity: int
    movement_type: MovementType
    reference_id: Optional[UUID] = None
    batch_number: Optional[str] = None
    reason: Optional[str] = None
    created_by: Optional[UUID] = None 