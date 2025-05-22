from enum import Enum
from typing import List


class ProductStatus(Enum):
    """
    Enum representing the possible statuses of a product in the pharmacy system.
    """
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    RECALLED = "RECALLED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    DRAFT="DRAFT"


    def __str__(self):
        return self.value
    
    
    @classmethod
    def available_statuses(cls) -> List[str]:
        """Return a list of statuses that indicate a product is available for sale"""
        return [cls.ACTIVE.value]
    
    @classmethod
    def unavailable_statuses(cls) -> List[str]:
        """Return a list of statuses that indicate a product is not available for sale"""
        return [
            cls.DRAFT.value,
            cls.INACTIVE.value,
            cls.DISCONTINUED.value,
            cls.OUT_OF_STOCK.value,
            cls.RECALLED.value,
            cls.PENDING_APPROVAL.value
        ] 