from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class UpdateHealthCareCenterCommand:
    """Command for updating a health care center"""
    id: UUID
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None
