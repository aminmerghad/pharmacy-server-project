from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class PaymentDetailsRequest(BaseModel):
    """Payment details for processing a payment."""
    payment_method: str
    amount: float
    transaction_id: Optional[str] = None
    payment_info: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProcessPaymentCommand(BaseModel):
    """Command for processing a payment for an invoice."""
    id: UUID
    payment_details: PaymentDetailsRequest 