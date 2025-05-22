from dataclasses import dataclass
from uuid import UUID

from app.services.order_service.domain.value_objects.order_status import OrderStatus


@dataclass
class UpdateOrderCommand():
    order_id: UUID
    new_status: OrderStatus
