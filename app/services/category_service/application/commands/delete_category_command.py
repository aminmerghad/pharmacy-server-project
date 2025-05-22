from dataclasses import dataclass
from uuid import UUID

@dataclass
class DeleteCategoryCommand:
    id: UUID 