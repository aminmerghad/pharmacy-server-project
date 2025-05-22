from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID
from app.services.auth_service.domain.value_objects import Password, Email

@dataclass
class UserEntity:
    """Entity representing a user in the system"""
    
    username: str
    password: Password  # Will be hashed by repository before storage
    email: str
    full_name: str
    phone: str
    is_admin: bool = False
    health_care_center_id: Optional[UUID] = None
    id: Optional[UUID] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def verify_password(self, plain_password: str) -> bool:
        """Verify if the provided password matches the user's password"""        
        return self.password.verify(plain_password)  # This will be replaced with proper hashing

    def mark_as_updated(self):
        self.updated_at = datetime.now(UTC)
    
    def deactivate(self):
        """Deactivate the user"""
        return UserEntity(
            id=self.id,
            username=self.username,
            password=self.password,
            email=self.email,
            full_name=self.full_name,
            phone=self.phone,
            is_admin=self.is_admin,
            health_care_center_id=self.health_care_center_id,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now(UTC)
        )
    
    def update(self, **kwargs):
        """Update user attributes"""
        return UserEntity(
            id=self.id,
            username=kwargs.get('username', self.username),
            password=kwargs.get('password', self.password),
            email=kwargs.get('email', self.email),
            full_name=kwargs.get('full_name', self.full_name),
            phone=kwargs.get('phone', self.phone),
            is_admin=kwargs.get('is_admin', self.is_admin),
            health_care_center_id=kwargs.get('health_care_center_id', self.health_care_center_id),
            is_active=kwargs.get('is_active', self.is_active),
            created_at=self.created_at,
            updated_at=datetime.now(UTC)
        ) 