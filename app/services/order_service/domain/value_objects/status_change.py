from dataclasses import dataclass
from datetime import datetime

from app.services.order_service.domain.value_objects import OrderStatus


@dataclass
class StatusChange:
    status: OrderStatus
    changed_at: datetime