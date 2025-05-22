from enum import Enum

class OrderStockStatus(Enum):
    """Internal order service stock status"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIALLY_AVAILABLE = "partially_available"
    
    @classmethod
    def from_inventory_status(cls, status: str) -> 'OrderStockStatus':
        """Map inventory service status to order service status"""
        status_mapping = {
            "in_stock": cls.AVAILABLE,
            "low_stock": cls.AVAILABLE,
            "out_of_stock": cls.UNAVAILABLE,
            "discontinued": cls.UNAVAILABLE,
            "reserved": cls.PARTIALLY_AVAILABLE,
            "pending": cls.PARTIALLY_AVAILABLE
        }
        return status_mapping.get(status, cls.UNAVAILABLE)

    def __str__(self) -> str:
        return self.value

    def to_json(self) -> str:
        return self.value