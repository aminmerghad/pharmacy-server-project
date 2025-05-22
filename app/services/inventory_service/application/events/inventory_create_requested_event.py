from uuid import UUID
from datetime import date
from typing import Optional

from pydantic import BaseModel


class InventoryCreateRequestedEvent(BaseModel):
    product_id:UUID
    price: float
    quantity: int
    max_stock: int
    min_stock: int        
    expiry_date:date    
    supplier_id: Optional[UUID] = None
