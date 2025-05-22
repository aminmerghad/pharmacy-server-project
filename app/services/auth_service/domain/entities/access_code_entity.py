from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID
import secrets
from typing import Optional

@dataclass
class AccessCodeEntity:
    """Entity representing an access code for user registration"""
    id: Optional[UUID]
    code: str    
    health_care_center_id: Optional[UUID]
    is_used: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def mark_as_used(self):
        """Mark the access code as used"""
        self.is_used=True
    
    def deactivate(self):
        """Deactivate the access code"""
        return AccessCodeEntity(
            id=self.id,
            code=self.code,
           
            health_care_center_id=self.health_care_center_id,
            is_used=self.is_used,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now(),
            expires_at=self.expires_at
        )
    
    def is_expired(self) -> bool:
        """Check if the access code is expired"""
        if not self.expires_at:
            return False
        return self.expires_at < datetime.now()

    @staticmethod
    def generate(expiry_hours: int = 36) -> 'AccessCodeEntity':
        return AccessCodeEntity(
            code=secrets.token_urlsafe(5),
            expires_at=datetime.now(UTC) + timedelta(hours=expiry_hours),
            created_at=datetime.now(UTC)
        )

    def is_valid(self) -> bool:
        return not self.is_used and datetime.now(UTC).timestamp() < self.expires_at.timestamp()

    def use(self) -> None:
        self.is_used = True 