from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.services.auth_service.domain.entities.access_code_entity import AccessCodeEntity

@dataclass
class AccessCodeDTO:
    """Base DTO for access code"""
    id: UUID
    code: str
    email: str
    phone: Optional[str]
    role: str
    health_care_center_id: Optional[UUID]
    health_care_center_name: Optional[str]
    is_used: bool
    is_active: bool
    created_at: str
    expires_at: str

@dataclass
class GenerateAccessCodeOutputDTO:
    """Output DTO for access code generation"""
    id: UUID
    code: str    
    is_active: bool
    expires_at: str
    created_at: str
    health_care_center_id: Optional[UUID]=None
    health_care_center_name: Optional[str]=None
    referral_email: Optional[str]=None
    referral_phone: Optional[str]=None
    health_care_center_email: Optional[str]=None
    health_care_center_phone: Optional[str]=None
    

@dataclass
class AccessCodeValidationOutputDTO:
    """Output DTO for access code validation"""
    access_code_entity: AccessCodeEntity
    is_valid: bool
    message: str
    health_care_center_name: Optional[str]
    

# Type alias for paginated response
PaginatedAccessCodeListDTO = Dict[str, Any] 