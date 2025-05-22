from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from app.services.invoice_service.domain.value_objects.money import Money

@dataclass
class InvoiceItem:
    """Entity representing an item within an invoice."""
    product_id: str
    description: str
    quantity: int
    unit_price: Money
    item_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate the invoice item after initialization."""
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
            
    @property
    def subtotal(self) -> Money:
        """Calculate the subtotal price for this item."""
        return self.unit_price * self.quantity
        
    def update_quantity(self, new_quantity: int) -> None:
        """Update the quantity of this invoice item."""
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        self.quantity = new_quantity
        
    def update_unit_price(self, new_price: Money) -> None:
        """Update the unit price of this invoice item."""
        self.unit_price = new_price
        
    def update_description(self, new_description: str) -> None:
        """Update the description of this invoice item."""
        if not new_description:
            raise ValueError("Description cannot be empty")
        self.description = new_description
        
    def __eq__(self, other):
        """Check if two invoice items are equal."""
        if not isinstance(other, InvoiceItem):
            return False
            
        # If they have IDs, compare by ID
        if self.item_id and other.item_id:
            return self.item_id == other.item_id
            
        # Otherwise, compare by properties
        return (
            self.product_id == other.product_id and
            self.description == other.description and
            self.quantity == other.quantity and
            self.unit_price == other.unit_price
        ) 