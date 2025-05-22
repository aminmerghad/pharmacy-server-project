from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from app.services.order_service.application.dtos.order_dto import CreateOrderItemDTO

@dataclass
class CreateOrderCommand:
    # user_id: UUID
    items: List[CreateOrderItemDTO]
    user_id: Optional[UUID] = None
    notes: Optional[str] = None 