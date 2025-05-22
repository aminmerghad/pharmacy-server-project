from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class AddressDTO:
    """Base DTO for address information"""
    id: UUID
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    is_active: bool
    building_number: Optional[str]
    apartment_number: Optional[str]
    additional_info: Optional[str]
    

@dataclass
class AddressDetailsDTO(AddressDTO):
    """Extended DTO with relationship information"""
    user_id: Optional[UUID]
    user_name: Optional[str]
    health_care_center_id: Optional[UUID]
    health_care_center_name: Optional[str]

@dataclass
class AddressListDTO:
    """Simplified DTO for list operations"""
    id: UUID
    full_address: str
    city: str
    state: str
    country: str
    is_active: bool 