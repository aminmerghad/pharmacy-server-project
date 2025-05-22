from dataclasses import dataclass
from uuid import UUID

@dataclass
class DeleteHealthCareCenterCommand:
    """Command for deleting (deactivating) a health care center"""
    id: UUID 