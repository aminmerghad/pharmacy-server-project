from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class GetCategoriesByFilterQuery(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True
    sort_by: str = "name"
    sort_direction: str = "asc"
    page: int = 1
    items_per_page: int = 20 