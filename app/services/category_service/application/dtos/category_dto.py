from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.shared.domain.exceptions.common_errors import ValidationError

class CategoryFieldsDto(BaseModel):
    name: str
    description: str
    id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    is_active: bool = True
    
    def validate(self) -> None:
        """Validate category fields"""
        if not self.name.strip():
            raise ValidationError("Name must not be empty.")
            
        if len(self.description) > 500:
            raise ValidationError("Description must not exceed 500 characters.")
            
        if self.image_url and len(self.image_url) > 255:
            raise ValidationError("Image URL must not exceed 255 characters.")

class CategoryResponseDto(BaseModel):
    id: UUID
    name: str
    description: str
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    is_active: bool

class CategoryListDto(BaseModel):
    items: List[CategoryResponseDto]
    total_items: int
    page: int
    page_size: int
    total_pages: int 