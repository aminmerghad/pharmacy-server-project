from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

class GetInvoicesByFilterQuery(BaseModel):
    """Query for retrieving lists of invoices with various filtering options."""
    
    user_id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    status: Optional[str] = None
    is_paid: Optional[bool] = None
    created_at_after: Optional[datetime] = None
    created_at_before: Optional[datetime] = None
    due_date_after: Optional[datetime] = None
    due_date_before: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    sort_by: str = "created_at"
    sort_direction: str = "desc"
    page: int = 1
    page_size: int = 20 