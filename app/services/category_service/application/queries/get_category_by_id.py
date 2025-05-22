from uuid import UUID
from pydantic import BaseModel

class GetCategoryByIdQuery(BaseModel):
    id: UUID 