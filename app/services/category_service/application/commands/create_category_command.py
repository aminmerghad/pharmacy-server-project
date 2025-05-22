from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.category_service.application.dtos.category_dto import CategoryFieldsDto
from app.shared.domain.exceptions.common_errors import ValidationError

@dataclass
class CreateCategoryCommand:
    category_fields: CategoryFieldsDto
    category_id: Optional[UUID] = None

    def __init__(self, **kwargs):
        category_data = kwargs.get('category_fields', {})

        if kwargs.get('category_id'):
            self.category_id = kwargs.get('category_id')
        
        self.category_fields = CategoryFieldsDto(**category_data)
        self.category_fields.validate() 