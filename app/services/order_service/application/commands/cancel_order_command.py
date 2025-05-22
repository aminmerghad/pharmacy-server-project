from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class CancelOrderCommand:
    order_id: UUID
    user_id:UUID
    reason: Optional[str] = None 