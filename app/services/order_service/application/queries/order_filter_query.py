from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID

@dataclass
class OrderFilterQuery:
    user_id: Optional[UUID] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    page: int = 1
    per_page: int = 10