from uuid import UUID
from pydantic import BaseModel


class GetInventoryByIdQuery(BaseModel):
    product_id: UUID