from dataclasses import dataclass
from typing import Optional

@dataclass
class OrderItem:
    product_id:str
    quantity:int

@dataclass
class OrderGetStockLevelQuery:
    cart_items : Optional[OrderItem]=[]
    

    
