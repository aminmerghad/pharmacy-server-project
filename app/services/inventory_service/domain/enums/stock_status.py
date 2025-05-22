from enum import Enum

class StockStatus(str,Enum):
    """Internal inventory service stock status"""
    OUT_OF_STOCK = "OUT_OF_STOCK"
    LOW_STOCK = "LOW_STOCK"
    DISCONTINUED = "DISCONTINUED"
    RESERVED = "RESERVED"
    AVAILABLE = "AVAILABLE"
    INACTIVE = "INACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"

    @classmethod
    def to_contract(cls, status: 'StockStatus') -> str:
        """Convert domain status to contract status"""
        return status.value
    
    @classmethod
    def from_contract(cls, status: str) -> 'StockStatus':
        """Convert contract status to domain status"""
        return cls(status)
    
    def validate(self, status: str) -> bool:
        return status in [
            StockStatus.IN_STOCK.value, 
            StockStatus.OUT_OF_STOCK.value, 
            StockStatus.LOW_STOCK.value]
    def __str__(self):
        return self.value