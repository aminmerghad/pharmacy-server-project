from dataclasses import dataclass,field
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


@dataclass
class CreateOrderItemDto:
    product_id:UUID = None
    unit_price:Decimal = Decimal(0)
    quantity:int=0




class CreateOrderCommand(BaseModel):
    user_id: UUID = None
    items: List[CreateOrderItemDto] = field(default_factory=list)
    total_amount: Decimal = None
    notes: Optional[str] = None

        


    

