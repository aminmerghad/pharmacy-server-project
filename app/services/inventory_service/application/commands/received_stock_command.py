from dataclasses import dataclass
@dataclass
class ReceivedStockCommand():
    product_id: int
    quantity: int
    # supplier: str
    # price: float
    # max_stock: int
    # min_stock: int