from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.entities.invoice_item import InvoiceItem
from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod

@dataclass
class InvoiceItemDTO:
    """Data Transfer Object for invoice items."""
    product_id: str
    description: str
    quantity: int
    unit_price: float
    subtotal: float
    item_id: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: InvoiceItem) -> 'InvoiceItemDTO':
        """Create DTO from domain entity."""
        return cls(
            product_id=entity.product_id,
            description=entity.description,
            quantity=entity.quantity,
            unit_price=float(entity.unit_price.amount),
            subtotal=float(entity.subtotal.amount),
            item_id=entity.item_id
        )

@dataclass
class PaymentDetailsDTO:
    """Data Transfer Object for payment details."""
    payment_method: str
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    payer_name: Optional[str] = None
    payment_reference: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: Optional[PaymentDetails]) -> Optional['PaymentDetailsDTO']:
        """Create DTO from domain entity."""
        if not entity:
            return None
            
        return cls(
            payment_method=entity.payment_method.value,
            transaction_id=entity.transaction_id,
            payment_date=entity.payment_date,
            payer_name=entity.payer_name,
            payment_reference=entity.payment_reference
        )

@dataclass
class InvoiceDTO:
    """Data Transfer Object for invoices."""
    invoice_id: str
    order_id: str
    user_id: str
    status: str
    items: List[InvoiceItemDTO]
    total_amount: float
    subtotal: float
    tax_amount: float
    discount_amount: float
    due_date: datetime
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    payment_details: Optional[PaymentDetailsDTO] = None
    notes: Optional[str] = None

    def get_payment_url(self) -> Optional[str]:
        """
        Get the payment URL for this invoice if available.
        
        Returns:
            The payment URL or None if not available
        """
        if self.payment_details and self.payment_details.payment_reference:
            return self.payment_details.payment_reference
        return None

    @classmethod
    def from_entity(cls, entity: Invoice) -> 'InvoiceDTO':
        """Create DTO from domain entity."""
        return cls(
            invoice_id=entity.invoice_id,
            order_id=entity.order_id,
            user_id=entity.user_id,
            status=entity.status.value,
            items=[InvoiceItemDTO.from_entity(item) for item in entity.items],
            total_amount=float(entity.total_amount.amount),
            subtotal=float(entity.subtotal.amount),
            tax_amount=float(entity.tax_amount.amount),
            discount_amount=float(entity.discount_amount.amount),
            due_date=entity.due_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            paid_at=entity.paid_at,
            payment_details=PaymentDetailsDTO.from_entity(entity.payment_details),
            notes=entity.notes
        )

@dataclass
class InvoiceListDTO:
    """Data Transfer Object for a paginated list of invoices."""
    items: List[InvoiceDTO]
    page: int
    page_size: int
    total_items: int
    total_pages: int

@dataclass
class CreateInvoiceItemDTO:
    """DTO for creating a new invoice item."""
    product_id: str
    description: str
    quantity: int
    unit_price: float
    
    def to_entity(self) -> InvoiceItem:
        """Convert to domain entity."""
        return InvoiceItem(
            product_id=self.product_id,
            description=self.description,
            quantity=self.quantity,
            unit_price=Money(self.unit_price)
        )

@dataclass
class CreateInvoiceDTO:
    """DTO for creating a new invoice."""
    order_id: str
    user_id: str
    items: List[CreateInvoiceItemDTO]
    due_date: datetime
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    notes: Optional[str] = None
    
    def to_entity(self) -> Invoice:
        """Convert to domain entity."""
        return Invoice(
            order_id=self.order_id,
            user_id=self.user_id,
            items=[item.to_entity() for item in self.items],
            due_date=self.due_date,
            tax_amount=Money(self.tax_amount),
            discount_amount=Money(self.discount_amount),
            notes=self.notes
        )

@dataclass
class UpdateInvoiceDTO:
    """DTO for updating an invoice."""
    due_date: Optional[datetime] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    notes: Optional[str] = None

@dataclass
class ProcessPaymentDTO:
    """DTO for processing a payment."""
    payment_method: str
    amount: float
    payment_info: Dict[str, Any]
    
    def to_domain_values(self) -> Dict[str, Any]:
        """Convert to domain values."""
        return {
            'payment_method': PaymentMethod(self.payment_method),
            'amount': Money(self.amount),
            'payment_info': self.payment_info
        } 