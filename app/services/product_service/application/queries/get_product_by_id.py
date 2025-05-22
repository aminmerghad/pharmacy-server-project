from uuid import UUID
from pydantic import BaseModel


class GetProductByIdQuery(BaseModel):
    id: UUID