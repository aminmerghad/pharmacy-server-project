from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.auth_service.application.dtos.access_code_dtos import (
    AccessCodeDTO, 
    AccessCodeValidationOutputDTO,
    PaginatedAccessCodeListDTO
)
from app.services.auth_service.application.queries.access_code.validate_access_code_query import ValidateAccessCodeQuery
from app.services.auth_service.application.queries.access_code.list_access_codes_query import ListAccessCodesQuery
from app.services.auth_service.domain.exceptions.access_code_errors import (
    AccessCodeNotFoundError,
    AccessCodeExpiredError,
    AccessCodeUsedError,
    AccessCodeInactiveError
)
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork


class AccessCodeQueryService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def validate_access_code(self, query: ValidateAccessCodeQuery) -> AccessCodeValidationOutputDTO:
        """Validate an access code and return validation result"""
        access_code = self._uow.access_code.get_by_code(query.code)
        if not access_code:
            return AccessCodeValidationOutputDTO(
                access_code_entity=None,
                health_care_center_name=None,
                is_valid=False,
                message="Access code not found"
            )

        if not access_code.is_active:
            return AccessCodeValidationOutputDTO(
                access_code_entity=access_code,
                health_care_center_name=self._get_center_name(access_code.health_care_center_id),
                is_valid=False,
                message="Access code is inactive"
            )
        
        if access_code.is_used:
            return AccessCodeValidationOutputDTO(
                access_code_entity=access_code,
                health_care_center_name=self._get_center_name(access_code.health_care_center_id),
                is_valid=False,
                message="Access code has already been used"
            )
        
        if access_code.is_expired():
            return AccessCodeValidationOutputDTO(
                access_code_entity=access_code,
                health_care_center_name=self._get_center_name(access_code.health_care_center_id),
                is_valid=False,
                message="Access code has expired"
            )
        
        # Access code is valid
        return AccessCodeValidationOutputDTO(
            access_code_entity=access_code,
            health_care_center_name=self._get_center_name(access_code.health_care_center_id),
            is_valid=True,
            message="Access code is valid"
        )
    
    def list_access_codes(self, query: ListAccessCodesQuery) -> PaginatedAccessCodeListDTO:
        """List access codes with filtering and pagination"""
        # Get all access codes
        access_codes = self._uow.access_code.get_all(active_only=False)
        
        # Apply filters
        filtered_codes = []
        for code in access_codes:
            # Apply is_active filter
            if query.is_active is not None and code.is_active != query.is_active:
                continue
                
            # Apply is_used filter
            if query.is_used is not None and code.is_used != query.is_used:
                continue
                
            # Apply email filter
            if query.email and query.email.lower() not in code.email.lower():
                continue
                
            # Apply role filter
            if query.role and query.role != code.role:
                continue
                
            # Apply search across multiple fields
            if query.search:
                search_term = query.search.lower()
                if (search_term not in code.code.lower() and 
                    search_term not in code.email.lower() and
                    (not code.phone or search_term not in code.phone.lower())):
                    continue
                    
            # If all filters pass, include this code
            filtered_codes.append(code)
        
        # Sort results
        if query.sort_by:
            reverse = query.sort_order.lower() == "desc"
            if query.sort_by == "created_at":
                filtered_codes.sort(key=lambda c: c.created_at, reverse=reverse)
            elif query.sort_by == "expires_at":
                filtered_codes.sort(key=lambda c: c.expires_at, reverse=reverse)
            elif query.sort_by == "code":
                filtered_codes.sort(key=lambda c: c.code, reverse=reverse)
            elif query.sort_by == "email":
                filtered_codes.sort(key=lambda c: c.email, reverse=reverse)
        
        # Apply pagination
        total_count = len(filtered_codes)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_codes = filtered_codes[start_idx:end_idx]
        
        # Convert to DTOs
        items = [self._to_dto(code) for code in paginated_codes]
        
        # Return paginated response
        return {
            "items": items,
            "total": total_count,
            "page": query.page,
            "page_size": query.page_size,
            "pages": (total_count + query.page_size - 1) // query.page_size if query.page_size > 0 else 1
        }
    
    def get_access_code_by_code(self, code: str) -> Optional[AccessCodeDTO]:
        """Get access code by code string"""
        access_code = self._uow.access_code.get_by_code(code)
        if not access_code:
            return None
        
        return self._to_dto(access_code)
    
    def _to_dto(self, access_code) -> Dict[str, Any]:
        """Convert entity to DTO"""
        return {
            "id": str(access_code.id) if access_code.id else None,
            "code": access_code.code,
            "email": access_code.email,
            "phone": access_code.phone,
            "role": access_code.role,
            "health_care_center_id": str(access_code.health_care_center_id) if access_code.health_care_center_id else None,
            "health_care_center_name": self._get_center_name(access_code.health_care_center_id),
            "is_used": access_code.is_used,
            "is_active": access_code.is_active,
            "created_at": access_code.created_at.isoformat() if access_code.created_at else None,
            "expires_at": access_code.expires_at.isoformat() if access_code.expires_at else None
        }
    
    def _get_center_name(self, center_id) -> Optional[str]:
        """Get the name of a health care center by ID"""
        if not center_id:
            return None
        
        center = self._uow.health_care_center.get_by_id(center_id)
        return center.name if center else None


