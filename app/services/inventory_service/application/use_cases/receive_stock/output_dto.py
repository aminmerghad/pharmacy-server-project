from dataclasses import dataclass
@dataclass
class ReceivedStockOutputDto:
    product_id: int
    quantity: int