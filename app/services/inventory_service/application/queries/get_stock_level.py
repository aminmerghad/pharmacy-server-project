from dataclasses import dataclass

@dataclass
class GetStockLevelQuery:
    product_id:str
    quantity:int

