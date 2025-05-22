from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from uuid import UUID

from .address_dtos import AddressListDTO
from .user_dtos import UserListDTO

@dataclass
class HealthCareCenterDTO:
    """Base DTO for health care center"""
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool

@dataclass
class HealthCareCenterListDTO:
    """DTO for list view of health care centers"""
    id: UUID
    name: str
    address: str
    email: str
    license_number: str
    is_active: bool

@dataclass
class HealthCareCenterDetailsDTO:
    """Detailed DTO for health care center"""
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool
    created_at: str
    updated_at: str

@dataclass
class HealthCareCenterSummaryDTO:
    """Summary DTO for health care center"""
    id: UUID
    name: str
    address: str
    is_active: bool

# Type alias for paginated response
PaginatedHealthCareCenterListDTO = Dict[str, Any] 