from dataclasses import dataclass
from uuid import UUID


@dataclass
class StockReceived:
    product_id:UUID
    quantity:int
