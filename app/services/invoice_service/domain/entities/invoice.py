from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.services.invoice_service.domain.entities.invoice_item import InvoiceItem
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails

@dataclass
class Invoice:
    """
    Invoice entity representing the aggregate root of the invoice domain.
    Manages the lifecycle and operations on an invoice.
    """
    order_id: str
    user_id: str
    items: List[InvoiceItem]
    due_date: datetime
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: InvoiceStatus = InvoiceStatus.PENDING
    tax_amount: Money = field(default_factory=lambda: Money(Decimal('0.00')))
    discount_amount: Money = field(default_factory=lambda: Money(Decimal('0.00')))
    payment_details: Optional[PaymentDetails] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate the invoice after initialization."""
        if not self.items:
            raise ValueError("Invoice must have at least one item")
            
        if self.due_date < self.created_at:
            raise ValueError("Due date cannot be earlier than creation date")
    
    @property
    def subtotal(self) -> Money:
        """Calculate the subtotal of all invoice items."""
        if not self.items:
            return Money(Decimal('0.00'))
            
        # Calculate the sum of all item subtotals
        return sum((item.subtotal for item in self.items), 
                  Money(Decimal('0.00')))
    
    @property
    def total_amount(self) -> Money:
        """Calculate the total amount including tax and discount."""
        total = self.subtotal
        
        # Add tax
        if self.tax_amount:
            total = total + self.tax_amount
            
        # Subtract discount
        if self.discount_amount:
            total = total - self.discount_amount
            
        return total
    
    @property
    def is_paid(self) -> bool:
        """Check if the invoice is paid."""
        return self.status == InvoiceStatus.PAID
    
    @property
    def is_cancelled(self) -> bool:
        """Check if the invoice is cancelled."""
        return self.status == InvoiceStatus.CANCELLED
    
    @property
    def is_overdue(self) -> bool:
        """Check if the invoice is overdue."""
        return self.status == InvoiceStatus.OVERDUE
    
    @property
    def is_pending(self) -> bool:
        """Check if the invoice is pending."""
        return self.status == InvoiceStatus.PENDING
    
    def add_item(self, item: InvoiceItem) -> None:
        """Add an item to the invoice."""
        if self.is_paid or self.is_cancelled:
            raise ValueError("Cannot modify items on a paid or cancelled invoice")
            
        self.items.append(item)
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: str) -> None:
        """Remove an item from the invoice."""
        if self.is_paid or self.is_cancelled:
            raise ValueError("Cannot modify items on a paid or cancelled invoice")
            
        original_length = len(self.items)
        self.items = [item for item in self.items if item.item_id != item_id]
        
        if len(self.items) == original_length:
            raise ValueError(f"Item with ID {item_id} not found in invoice")
            
        if not self.items:
            raise ValueError("Invoice must have at least one item")
            
        self.updated_at = datetime.now()
    
    def update_item(self, item_id: str, **kwargs) -> None:
        """Update an item in the invoice."""
        if self.is_paid or self.is_cancelled:
            raise ValueError("Cannot modify items on a paid or cancelled invoice")
            
        for item in self.items:
            if item.item_id == item_id:
                if 'quantity' in kwargs:
                    item.update_quantity(kwargs['quantity'])
                if 'unit_price' in kwargs:
                    item.update_unit_price(kwargs['unit_price'])
                if 'description' in kwargs:
                    item.update_description(kwargs['description'])
                self.updated_at = datetime.now()
                return
                
        raise ValueError(f"Item with ID {item_id} not found in invoice")
    
    def apply_tax(self, tax_amount: Money) -> None:
        """Apply tax to the invoice."""
        if self.is_paid or self.is_cancelled:
            raise ValueError("Cannot modify tax on a paid or cancelled invoice")
            
        self.tax_amount = tax_amount
        self.updated_at = datetime.now()
    
    def apply_discount(self, discount_amount: Money) -> None:
        """Apply a discount to the invoice."""
        if self.is_paid or self.is_cancelled:
            raise ValueError("Cannot modify discount on a paid or cancelled invoice")
            
        if discount_amount > self.subtotal:
            raise ValueError("Discount amount cannot be greater than subtotal")
            
        self.discount_amount = discount_amount
        self.updated_at = datetime.now()
    
    def mark_as_paid(self, payment_details: PaymentDetails) -> None:
        """Mark the invoice as paid."""
        if self.is_cancelled:
            raise ValueError("Cannot mark a cancelled invoice as paid")
            
        if self.is_paid:
            raise ValueError("Invoice is already paid")
            
        if not payment_details.is_payment_complete():
            raise ValueError("Payment details are incomplete")
            
        self.status = InvoiceStatus.PAID
        self.payment_details = payment_details
        self.paid_at = datetime.now()
        self.updated_at = datetime.now()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the invoice."""
        if self.is_paid:
            raise ValueError("Cannot cancel a paid invoice")
            
        if self.is_cancelled:
            raise ValueError("Invoice is already cancelled")
            
        self.status = InvoiceStatus.CANCELLED
        if reason:
            self.add_notes(reason)
        self.updated_at = datetime.now()
    
    def process_payment(self, payment_details: PaymentDetails) -> None:
        """
        Process a payment for the invoice.
        
        This method is called when a payment is being processed but may not be complete yet.
        If the payment is already complete, it marks the invoice as paid.
        Otherwise, it updates the payment details for future verification.
        
        Args:
            payment_details: The details of the payment
        """
        if self.is_cancelled:
            raise ValueError("Cannot process payment for a cancelled invoice")
            
        if self.is_paid:
            raise ValueError("Invoice is already paid")
            
        # Store the payment details regardless
        self.payment_details = payment_details
        self.updated_at = datetime.now()
        
        # If the payment is already confirmed as complete, mark as paid
        if payment_details.is_payment_complete():
            self.status = InvoiceStatus.PAID
            self.paid_at = payment_details.payment_date or datetime.now()
    
    def mark_as_overdue(self) -> None:
        """Mark the invoice as overdue."""
        if not self.is_pending:
            raise ValueError("Only pending invoices can be marked as overdue")
            
        if datetime.now() < self.due_date:
            raise ValueError("Invoice is not yet due")
            
        self.status = InvoiceStatus.OVERDUE
        self.updated_at = datetime.now()
    
    def extend_due_date(self, days: int) -> None:
        """Extend the due date by a number of days."""
        if self.is_paid or self.is_cancelled:
            raise ValueError("Cannot modify due date on a paid or cancelled invoice")
            
        if days <= 0:
            raise ValueError("Extension days must be positive")
            
        self.due_date = self.due_date + timedelta(days=days)
        
        # If invoice was overdue but now has a future due date, change status back to pending
        if self.is_overdue and self.due_date > datetime.now():
            self.status = InvoiceStatus.PENDING
            
        self.updated_at = datetime.now()
    
    def add_notes(self, notes: str) -> None:
        """Add notes to the invoice."""
        if not notes:
            raise ValueError("Notes cannot be empty")
            
        self.notes = notes
        self.updated_at = datetime.now() 