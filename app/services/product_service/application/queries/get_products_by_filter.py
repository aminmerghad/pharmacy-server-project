from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

class GetProductsByFilterQuery(BaseModel):
    name: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    is_prescription_required: Optional[bool] = None
    is_active: bool = True
    min_stock: Optional[int] = None
    has_stock: Optional[bool] = None
    sort_by: str = "name"
    sort_direction: str = "asc"
    page: int = 1
    items_per_page: int = 20