from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class GetInvoiceQuery(BaseModel):
    """Query for retrieving a single invoice by ID."""
    
    id: UUID 