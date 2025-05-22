from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class CategoryEntity(BaseModel):
    name: str
    description: str
    id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True 