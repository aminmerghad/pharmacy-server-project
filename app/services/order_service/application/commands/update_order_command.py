from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.order_service.domain.value_objects.order_status import OrderStatus

@dataclass
class UpdateOrderCommand:
    id: UUID
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None 