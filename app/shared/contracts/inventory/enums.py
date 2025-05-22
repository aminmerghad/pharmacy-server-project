from enum import Enum

class StockStatusContract(str, Enum):
    """
    Enumeration of possible stock statuses
    
    This enum represents all possible validation statuses for inventory items
    when performing stock checks, including combined statuses.
    """
    AVAILABLE = "AVAILABLE"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"
    
    # Combined status for items that are both low on stock and expiring soon
    
    @classmethod
    def get_unavailable_statuses(cls):
        """Get a list of statuses that indicate stock is unavailable"""
        return [
            cls.OUT_OF_STOCK,
            cls.INSUFFICIENT_STOCK,
            cls.EXPIRED,
            cls.INACTIVE
        ]
    
    @classmethod
    def get_warning_statuses(cls):
        """Get a list of statuses that indicate warnings but stock is available"""
        return [
            cls.LOW_STOCK,
            cls.EXPIRING_SOON,
        ]
    
    @property
    def is_warning(self):
        """Check if status is a warning status"""
        return self in self.get_warning_statuses()
    
    @property
    def is_unavailable(self):
        """Check if status indicates unavailability"""
        return self in self.get_unavailable_statuses()