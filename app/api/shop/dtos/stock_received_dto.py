
from pydantic import BaseModel


class ReceivedStockDto(BaseModel):
    product_id: int
    quantity: int