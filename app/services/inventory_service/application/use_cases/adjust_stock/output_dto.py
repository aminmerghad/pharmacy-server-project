from dataclasses import dataclass
from uuid import UUID


@dataclass
class AdjustStockOutputDto:
    """
    Output DTO for stock adjustment operations.
    
    Contains the result of a stock adjustment operation including
    the previous and new quantities for audit tracking.
    """
    inventory_id: UUID
    product_id: UUID
    previous_quantity: int
    adjustment_quantity: int
    new_quantity: int
    reason: str
    movement_id: UUID
    
    def to_json(self):
        """
        Convert the DTO to a dictionary suitable for JSON serialization.
        """
        return {
            "inventory_id": str(self.inventory_id),
            "product_id": str(self.product_id),
            "previous_quantity": self.previous_quantity,
            "adjustment_quantity": self.adjustment_quantity,
            "new_quantity": self.new_quantity,
            "reason": self.reason,
            "movement_id": str(self.movement_id)
        } 