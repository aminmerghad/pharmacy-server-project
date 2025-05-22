from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod

@dataclass(frozen=True)
class PaymentDetails:
    """Value object representing payment details for an invoice."""
    payment_method: PaymentMethod
    amount: Optional[float] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    payer_name: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate payment details."""
        if self.transaction_id and not isinstance(self.transaction_id, str):
            raise ValueError("Transaction ID must be a string")
            
        if self.payment_date and not isinstance(self.payment_date, datetime):
            raise ValueError("Payment date must be a datetime object")

    def is_payment_complete(self) -> bool:
        """
        Check if payment has been completed.
        
        A payment is considered complete if it has a transaction ID and payment date.
        Some payment methods may be pending confirmation and thus not complete yet.
        """
        return self.transaction_id is not None and self.payment_date is not None
    
    def get_payment_url(self) -> Optional[str]:
        """
        Get the URL where the customer can complete the payment.
        
        Returns:
            Payment URL if available, None otherwise
        """
        return self.payment_reference
        
    def __str__(self):
        """String representation of payment details."""
        if self.is_payment_complete():
            return f"Payment: {self.payment_method.value} (ID: {self.transaction_id}, Date: {self.payment_date})"
        return f"Payment method: {self.payment_method.value} (pending)" 