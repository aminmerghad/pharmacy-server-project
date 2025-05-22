from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from .address_dtos import AddressListDTO

@dataclass
class UserDTO:
    """Data Transfer Object for user information"""
    id: UUID
    username: str
    email: str
    full_name: str
    phone: str
    role: str
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None    
    health_care_center_name: Optional[str] = None
    health_care_center_id: Optional[UUID] = None
    

@dataclass
class UserDetailsDTO(UserDTO):
    """Extended DTO with relationship information"""    
    created_at: str
    updated_at: str
    last_login: Optional[str]=None
    health_care_center_id: Optional[UUID]=None
    health_care_center_name: Optional[str]=None
    
    addresses: Optional[List[AddressListDTO]]=None
    
    

@dataclass
class UserListDTO:
    """Simplified DTO for list operations"""
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool

@dataclass
class UserAuthDTO:
    """DTO for authentication responses"""
    id: UUID
    email: str
    name: str
    role: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@dataclass
class UserRegistrationDTO:
    """DTO for user registration requests"""
    email: str
    password: str
    name: str
    role: str
    health_care_center_id: Optional[UUID] = None

@dataclass
class UserUpdateDTO:
    """DTO for user update requests"""
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    health_care_center_id: Optional[UUID] = None

@dataclass
class UserRegisteredOutputDTO:
    """DTO returned after successful user registration"""
    id: UUID
    username: str
    email: str
    full_name: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime
    health_care_center_id: Optional[UUID]
    health_care_center_name: Optional[str]
    

@dataclass
class UserLoginOutputDTO:
    """DTO returned after successful user login"""
    id: UUID
    username: str
    email: str
    full_name: str
    phone: str
    role: str
    access_token: str
    refresh_token: str
    health_care_center_id: Optional[UUID]
    health_care_center_name: Optional[str]
    

PaginatedUserListType = Dict[str, Any]  # { items: List[UserDTO], total: int, page: int, page_size: int, pages: int } 