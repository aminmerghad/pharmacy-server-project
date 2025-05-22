from enum import Enum, auto

class InvoiceStatus(str, Enum):
    """Enumeration of possible invoice statuses."""
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE" 