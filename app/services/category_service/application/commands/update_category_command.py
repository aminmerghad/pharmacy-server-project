from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.category_service.application.dtos.category_dto import CategoryFieldsDto
from app.shared.domain.exceptions.common_errors import ValidationError

@dataclass
class UpdateCategoryCommand:
    id: UUID
    category_fields: CategoryFieldsDto

    def __init__(self, **kwargs):
        if not kwargs.get('id'):
            raise ValidationError("Category ID is required for updates")
        
        self.id = kwargs.get('id')
        category_data = kwargs.get('category_fields', {})
        
        self.category_fields = CategoryFieldsDto(**category_data)
        self.category_fields.validate() 