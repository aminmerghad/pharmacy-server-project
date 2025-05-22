from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class CancelInvoiceCommand(BaseModel):
    """Command for cancelling an invoice"""
    
    id: UUID
    reason: Optional[str] = None 