from enum import Enum

class MovementType(str, Enum):
    """
    Types of inventory movements in a pharmacy system.
    
    Each movement type represents a different business operation that affects inventory levels.
    This allows for detailed tracking and reporting of inventory changes.
    """
    # Additions to inventory
    RECEIVED = "RECEIVED"                 # Stock received from supplier
    RETURNED = "RETURNED"                 # Stock returned by customer
    ADJUSTMENT_INCREASE = "ADJUSTMENT_INCREASE"  # Manual adjustment to increase stock
    
    # Reductions from inventory
    DISPENSED = "DISPENSED"               # Stock dispensed to customer
    EXPIRED = "EXPIRED"                   # Stock removed due to expiration
    DAMAGED = "DAMAGED"                   # Stock damaged or destroyed
    TRANSFERRED_OUT = "TRANSFERRED_OUT"   # Stock transferred to another location
    ADJUSTMENT_DECREASE = "ADJUSTMENT_DECREASE"  # Manual adjustment to decrease stock
    
    # Transfers (may be combined with TRANSFERRED_OUT + RECEIVED)
    TRANSFERRED_IN = "TRANSFERRED_IN"     # Stock received from another location
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def requires_reference(cls, movement_type: 'MovementType') -> bool:
        """
        Check if this type of movement requires a reference ID.
        (e.g., an order ID, transfer ID, etc.)
        """
        return movement_type in [
            MovementType.DISPENSED,
            MovementType.TRANSFERRED_OUT,
            MovementType.TRANSFERRED_IN,
            MovementType.RETURNED
        ]
    
    @classmethod
    def requires_reason(cls, movement_type: 'MovementType') -> bool:
        """
        Check if this type of movement requires a reason.
        """
        return movement_type in [
            MovementType.ADJUSTMENT_INCREASE,
            MovementType.ADJUSTMENT_DECREASE,
            MovementType.DAMAGED
        ] 