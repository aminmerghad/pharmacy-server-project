from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class HealthCareCenterEntity:
    id: Optional[UUID]
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def update(self, name=None, address=None, phone=None, email=None, license_number=None):
        """Update health care center properties"""
        return HealthCareCenterEntity(
            id=self.id,
            name=name if name is not None else self.name,
            address=address if address is not None else self.address,
            phone=phone if phone is not None else self.phone,
            email=email if email is not None else self.email,
            license_number=license_number if license_number is not None else self.license_number,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
    
    def deactivate(self):
        """Deactivate a health care center"""
        return HealthCareCenterEntity(
            id=self.id,
            name=self.name,
            address=self.address,
            phone=self.phone,
            email=self.email,
            license_number=self.license_number,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now()
        ) 