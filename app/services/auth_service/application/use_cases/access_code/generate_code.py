import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.services.auth_service.application.commands.access_code.generate_access_code_command import GenerateAccessCodeCommand
from app.services.auth_service.application.dtos.access_code_dtos import GenerateAccessCodeOutputDTO
from app.services.auth_service.domain.entities.access_code_entity import AccessCodeEntity
from app.services.auth_service.domain.exceptions.health_care_center_errors import HealthCareCenterNotFoundError
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

@dataclass
class AccessCodeDTO:
    code: str
    expires_at: str

class GenerateAccessCodeUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    def execute(self, command: GenerateAccessCodeCommand) -> GenerateAccessCodeOutputDTO:
        """Generate a new access code for user registration"""
        
        # Determine health care center ID
        health_care_center_id = self._resolve_health_care_center_id(
            health_care_center_email=command.health_care_center_email,
            health_care_center_phone=command.health_care_center_phone,
            referral_email=command.referral_email,
            referral_phone=command.referral_phone
        )
        
        # Generate a random access code
        code = self._generate_random_code()
        
        # Calculate expiry date
        expiry_date = datetime.now() + timedelta(days=command.expiry_days)
        
        # Create access code entity
        access_code = AccessCodeEntity(
            id=None,
            code=code,            
            health_care_center_id=health_care_center_id,
            is_used=False,
            is_active=True,
            created_at=None,
            updated_at=None,
            expires_at=expiry_date
        )
        # Save to repository
        created_access_code = self._uow.access_code.add(access_code)
        self._uow.commit()
        
        # Get health care center name if present
        health_care_center_name = None
        health_care_center_email = None
        health_care_center_phone = None
        if health_care_center_id:
            health_care_center = self._uow.health_care_center.get_by_id(health_care_center_id)
            if health_care_center:
                health_care_center_name = health_care_center.name
                health_care_center_email = health_care_center.email
                health_care_center_phone = health_care_center.phone


        # Return output DTO
        return GenerateAccessCodeOutputDTO(
            id=created_access_code.id,
            code=created_access_code.code,
            referral_email=command.referral_email,
            referral_phone=command.referral_phone,
            health_care_center_email=health_care_center_email,
            health_care_center_phone=health_care_center_phone,
            health_care_center_id=health_care_center_id,
            health_care_center_name=health_care_center_name,
            is_active=created_access_code.is_active,
            expires_at=created_access_code.expires_at.isoformat() if created_access_code.expires_at else None,
            created_at=created_access_code.created_at.isoformat() if created_access_code.created_at else None
        )
    
    def _generate_random_code(self, length: int = 8) -> str:
        """Generate a random alphanumeric code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _resolve_health_care_center_id(
        self, 
        health_care_center_email: Optional[str] = None,
        health_care_center_phone: Optional[str] = None,
        referral_email: Optional[str] = None,
        referral_phone: Optional[str] = None
    ) -> Optional[UUID]:
        """Resolve health care center ID from the provided information"""
        if referral_email:
            user = self._uow.user.get_by_email(referral_email)
            if user:
                if(user.health_care_center_id is None):
                    raise HealthCareCenterNotFoundError("Health care center not found for user")
                return user.health_care_center_id
        if referral_phone:
            user = self._uow.user.get_by_phone(referral_phone)
            if user:
                if(user.health_care_center_id is None):
                    raise HealthCareCenterNotFoundError("Health care center not found for user")
                return user.health_care_center_id    
        if referral_email or referral_phone:
            message = "Health care center not found with provided "
            if referral_email:
                message += f"email: {referral_email}"
            if referral_phone:
                message += f"{' and ' if referral_email else ''}phone: {referral_phone}"
            raise HealthCareCenterNotFoundError(message)
        # If email is provided, try to find by email
        if health_care_center_email:
            center = self._uow.health_care_center.get_by_email(health_care_center_email)
            if center:
                if(center.id is None):
                    raise HealthCareCenterNotFoundError("Health care center not found")
                return center.id
        
        # If phone is provided, try to find by phone
        if health_care_center_phone:
            # Assuming there's a method to get by phone
            center = self._uow.health_care_center.get_by_phone(health_care_center_phone)
            if center:
                if(center.id is None):
                    raise HealthCareCenterNotFoundError("Health care center not found")
                return center.id
        
        # No valid health care center found
        if health_care_center_email or health_care_center_phone:
            message = "Health care center not found with provided "
            if health_care_center_email:
                message += f"email: {health_care_center_email}"
            if health_care_center_phone:
                message += f"{' and ' if health_care_center_email else ''}phone: {health_care_center_phone}"
            raise HealthCareCenterNotFoundError(message)
        
        # No health care center info provided, return None
        return None       
        
   